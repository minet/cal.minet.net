import re
from collections.abc import Iterable

from sqlmodel import Session, select

from app.models import LDAPUser, Membership, Organization, Role, User


def is_member_visible(
    viewer_year: int | None,
    can_view_all: bool,
    organization_restrictions: set[int],
    member_restrictions: set[int],
) -> bool:
    if can_view_all:
        return True
    restricted_years = organization_restrictions | member_restrictions
    if viewer_year is None:
        return not restricted_years
    return viewer_year not in restricted_years


def _organization_restrictions(organization: Organization) -> set[int]:
    return {
        year
        for year in (1, 2, 3)
        if getattr(organization, f"hide_members_from_year_{year}")
    }


def _membership_restrictions(membership: Membership) -> set[int]:
    return {year for year in (1, 2, 3) if getattr(membership, f"hide_from_year_{year}")}


def _viewer_can_view_all(
    session: Session, organization: Organization, viewer: User | None
) -> bool:
    if viewer is None:
        return False
    if viewer.is_superadmin:
        return True
    own_membership = session.exec(
        select(Membership).where(
            Membership.user_id == viewer.id,
            Membership.organization_id == organization.id,
        )
    ).first()
    if own_membership:
        return True
    if organization.parent_id:
        parent_admin = session.exec(
            select(Membership).where(
                Membership.user_id == viewer.id,
                Membership.organization_id == organization.parent_id,
                Membership.role == Role.ORG_ADMIN,
            )
        ).first()
        if parent_admin:
            return True
    return False


def _viewer_student_year(session: Session, viewer: User | None) -> int | None:
    if viewer is None:
        return None
    ldap_user = session.exec(
        select(LDAPUser).where(LDAPUser.email == viewer.email)
    ).first()
    return ldap_user.student_year if ldap_user else None


def visible_memberships(
    session: Session,
    organization: Organization,
    viewer: User | None,
    memberships: Iterable[Membership],
) -> list[Membership]:
    """Return the roster visible to a viewer under all confidentiality rules."""
    can_view_all = _viewer_can_view_all(session, organization, viewer)
    viewer_year = None if can_view_all else _viewer_student_year(session, viewer)
    organization_restrictions = _organization_restrictions(organization)
    return [
        membership
        for membership in memberships
        if is_member_visible(
            viewer_year,
            can_view_all,
            organization_restrictions,
            _membership_restrictions(membership),
        )
    ]


def normalize_student_year(raw_values: object) -> int | None:
    """Normalize SupAnn cursus-year values to the application's 1A/2A/3A groups."""
    if raw_values is None:
        return None
    if isinstance(raw_values, str):
        values: Iterable[object] = [raw_values]
    elif isinstance(raw_values, Iterable):
        values = raw_values
    else:
        values = [raw_values]

    years = set()
    for raw_value in values:
        value = str(raw_value).strip()
        value = re.sub(r"^\{[^}]+\}", "", value)
        match = re.fullmatch(
            r"(?:([123])A?|A([123])|ING([123])|[XLM]([123]))",
            value,
            re.IGNORECASE,
        )
        if not match:
            match = re.search(
                r"(?:^|[-_])(?:EI|EM|BACHELOR)([123])",
                value,
                re.IGNORECASE,
            )
        if not match:
            match = re.search(
                r"(?:^|[-_])(?:FIPA-?|DANI|DATAPAC|EOE|M)([123])$",
                value,
                re.IGNORECASE,
            )
        if match:
            years.add(int(next(group for group in match.groups() if group)))

    return years.pop() if len(years) == 1 else None
