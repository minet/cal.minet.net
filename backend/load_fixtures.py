#!/usr/bin/env python3
import json
import sys
import os
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any
from sqlmodel import Session, select
from app.database import engine
from app.models import (
    User, Organization, OrganizationType, Role, Tag, Event, 
    EventVisibility, Subscription, Group, Membership, EventTag
)

def load_json(filename: str):
    with open(filename, "r") as f:
        return json.load(f)

def load_fixtures(target_email: str, fixtures_dir: str = "fixtures"):
    print(f"Loading fixtures from {fixtures_dir}...")
    
    users_data = load_json(os.path.join(fixtures_dir, "users.json"))
    orgs_data = load_json(os.path.join(fixtures_dir, "organizations.json"))
    memberships_data = load_json(os.path.join(fixtures_dir, "memberships.json"))
    subscriptions_data = load_json(os.path.join(fixtures_dir, "subscriptions.json"))

    # Replace first user's email with target_email
    if users_data:
        original_email = users_data[0]["email"]
        print(f"Replacing primary user '{original_email}' with '{target_email}'")
        users_data[0]["email"] = target_email
        
        # Helper to replace email in other datasets
        def replace_email(data_list, key="user_email"):
            for item in data_list:
                if item.get(key) == original_email:
                    item[key] = target_email
        
        replace_email(memberships_data)
        replace_email(subscriptions_data)
    
    with Session(engine) as session:
        # 1. Create Users
        print("Creating users...")
        users_map = {}
        for user_data in users_data:
            user = session.exec(select(User).where(User.email == user_data["email"])).first()
            if not user:
                user = User(
                    email=user_data["email"],
                    full_name=user_data["full_name"],
                    is_superadmin=user_data.get("is_superadmin", False)
                )
                session.add(user)
                session.commit()
                session.refresh(user)
                print(f"  Created user: {user.email}")
            else:
                print(f"  User already exists: {user.email}")
            users_map[user.email] = user

        # 2. Create Organizations, Tags, Groups, Events
        print("Creating organizations and related data...")
        for org_data in orgs_data:
            org = session.exec(select(Organization).where(Organization.slug == org_data["slug"])).first()
            if not org:
                org = Organization(
                    name=org_data["name"],
                    slug=org_data["slug"],
                    type=OrganizationType(org_data["type"]),
                    description=org_data["description"],
                    logo_url=org_data.get("logo_url"),
                    color_chroma=org_data.get("color_chroma"),
                    color_hue=org_data.get("color_hue")
                )
                session.add(org)
                session.commit()
                session.refresh(org)
                print(f"  Created organization: {org.name}")
            else:
                print(f"  Organization already exists: {org.name}")

            # Tags
            tags_map = {}
            for tag_data in org_data.get("tags", []):
                tag = session.exec(select(Tag).where(Tag.name == tag_data["name"], Tag.organization_id == org.id)).first()
                if not tag:
                    tag = Tag(
                        name=tag_data["name"],
                        color=tag_data["color"],
                        organization_id=org.id
                    )
                    session.add(tag)
                    session.commit()
                    session.refresh(tag)
                tags_map[tag.name] = tag

            # Groups
            for group_data in org_data.get("groups", []):
                group = session.exec(select(Group).where(Group.name == group_data["name"], Group.organization_id == org.id)).first()
                if not group:
                    group = Group(
                        name=group_data["name"],
                        organization_id=org.id
                    )
                    session.add(group)
                    session.commit()

            # Events
            for event_data in org_data.get("events", []):
                # Determine creator - default to target_email user or first user
                creator_email = users_data[0]["email"]
                creator = users_map.get(creator_email)
                
                if not creator:
                    # Fallback to any user
                    creator = list(users_map.values())[0]

                start_time = datetime.now(timezone.utc) + timedelta(days=event_data["start_days_offset"])
                end_time = datetime.now(timezone.utc) + timedelta(days=event_data["end_days_offset"], hours=event_data["duration"])
                
                # Check if event exists (by title and org)
                event = session.exec(select(Event).where(Event.title == event_data["title"], Event.organization_id == org.id)).first()
                if not event:
                    visibility = EventVisibility(event_data["visibility"])
                    
                    # Set approved_at for approved events
                    approved_at = None
                    if visibility == EventVisibility.PUBLIC_APPROVED:
                        approved_at = datetime.now(timezone.utc)
                    
                    event = Event(
                        title=event_data["title"],
                        description=event_data["description"],
                        start_time=start_time,
                        end_time=end_time,
                        location=event_data["location"],
                        visibility=visibility,
                        organization_id=org.id,
                        created_by_id=creator.id,
                        hide_details=event_data.get("hide_details", False),
                        rejection_message=event_data.get("rejection_message"),
                        approved_at=approved_at
                    )
                    session.add(event)
                    session.commit()
                    session.refresh(event)
                    
                    # Add tags
                    for tag_name in event_data.get("tag_names", []):
                        if tag_name in tags_map:
                            event_tag = EventTag(event_id=event.id, tag_id=tags_map[tag_name].id)
                            session.add(event_tag)
                    session.commit()

        # 3. Memberships
        print("Creating memberships...")
        for mem_data in memberships_data:
            user = users_map.get(mem_data["user_email"])
            if not user:
                print(f"  Warning: User {mem_data['user_email']} not found for membership")
                continue
            
            org = session.exec(select(Organization).where(Organization.slug == mem_data["org_slug"])).first()
            if not org:
                print(f"  Warning: Org {mem_data['org_slug']} not found for membership")
                continue

            role = Role(mem_data["role"])
            membership = session.exec(select(Membership).where(Membership.user_id == user.id, Membership.organization_id == org.id)).first()
            if not membership:
                membership = Membership(
                    user_id=user.id,
                    organization_id=org.id,
                    role=role
                )
                session.add(membership)
                print(f"  Assigned {user.email} as {role} of {org.name}")
            else:
                if membership.role != role:
                    membership.role = role
                    session.add(membership)
                    print(f"  Updated {user.email} as {role} of {org.name}")
            session.commit()

        # 4. Subscriptions
        print("Creating subscriptions...")
        for sub_data in subscriptions_data:
            user = users_map.get(sub_data["user_email"])
            if not user:
                continue
            
            org = session.exec(select(Organization).where(Organization.slug == sub_data["org_slug"])).first()
            if not org:
                continue

            sub = session.exec(select(Subscription).where(Subscription.user_id == user.id, Subscription.organization_id == org.id)).first()
            if not sub:
                sub = Subscription(
                    user_id=user.id,
                    organization_id=org.id,
                    subscribe_all=True
                )
                session.add(sub)
                session.commit()
                print(f"  Subscribed {user.email} to {org.name}")

    print("Fixtures loaded successfully!")

def reset_database():
    print("Resetting database...")
    from app.models import SQLModel
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    print("Database reset complete.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Load fixtures into the database")
    parser.add_argument("email", help="Target user email")
    parser.add_argument("--reset", action="store_true", help="Reset database before loading")
    args = parser.parse_args()
    
    if args.reset:
        reset_database()
    
    target_email = args.email
    # Adjust path if running from root
    fixtures_dir = "backend/fixtures"
    if not os.path.exists(fixtures_dir):
        fixtures_dir = "fixtures"
        
    load_fixtures(target_email, fixtures_dir)
