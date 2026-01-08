#!/usr/bin/env python3
"""
CLI command to promote a user to superadmin
Usage: python make_superadmin.py <email>
"""

import sys
from sqlmodel import Session, select
from app.database import engine
from app.models import User


def make_superadmin(email: str):
    """Promote a user to superadmin by email"""
    with Session(engine) as session:
        # Find user by email
        user = session.exec(select(User).where(User.email == email)).first()
        
        if not user:
            print(f"❌ Error: User with email '{email}' not found")
            return False
        
        if user.is_superadmin:
            print(f"ℹ️  User '{email}' is already a superadmin, making it a regular user")
            user.is_superadmin = False
            session.add(user)
            session.commit()
            return True
        else:
            # Promote to superadmin
            user.is_superadmin = True
            session.add(user)
            session.commit()
        
        print(f"✅ Success: User '{email}' is now a superadmin")
        return True


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python make_superadmin.py <email>")
        print("Example: python make_superadmin.py user@example.com")
        sys.exit(1)
    
    email = sys.argv[1]
    success = make_superadmin(email)
    sys.exit(0 if success else 1)
