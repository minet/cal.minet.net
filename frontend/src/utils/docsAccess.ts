/**
 * Access logic for the in-app documentation.
 *
 * Mirrors the backend changelog audience system
 * (backend/app/api/changelogs.py::_user_matches_audience): a doc declares an
 * `audience` in its frontmatter, and a user can act on it depending on their
 * highest permission across all the organisations they belong to.
 */
import { Role } from '@/api/types'
import type { MembershipWithOrganization } from '@/api/types'

/** Who a guide concerns. Shown as a badge, purely informative. */
export type DocScope = 'application' | 'organisation' | 'personne'

/** Permission required to perform the action a guide describes. */
export type DocAudience =
  | 'all'
  | 'org_viewer_plus'
  | 'org_member_plus'
  | 'org_admin_plus'
  | 'treasury'
  | 'superadmin'

export interface UserAccess {
  isSuperadmin: boolean
  /** Highest org role held in any organisation, or null if member of none. */
  highestRole: Role | null
  /** True if the user can manage payment forms (treasury) in at least one org. */
  hasTreasury: boolean
}

/** A minimal org reference used to link to organisation pages. */
export interface OrgRef {
  id: string
  name: string
}

const ROLE_RANK: Record<Role, number> = {
  [Role.ORG_VIEWER]: 1,
  [Role.ORG_MEMBER]: 2,
  [Role.ORG_ADMIN]: 3,
}

type MaybeUser = { is_superadmin?: boolean } | null | undefined

/** Compute the user's highest permission across all their organisations. */
export function computeHighestAccess(
  user: MaybeUser,
  memberships: MembershipWithOrganization[],
): UserAccess {
  let highestRole: Role | null = null
  for (const m of memberships) {
    if (highestRole === null || ROLE_RANK[m.role] > ROLE_RANK[highestRole]) {
      highestRole = m.role
    }
  }
  return {
    isSuperadmin: user?.is_superadmin ?? false,
    highestRole,
    hasTreasury: memberships.some((m) => m.organization?.can_manage_payment_forms === true),
  }
}

/** Whether the user is allowed to act on a guide with the given audience. */
export function canAccess(audience: DocAudience, access: UserAccess): boolean {
  if (access.isSuperadmin) return true
  switch (audience) {
    case 'all':
      return true
    case 'org_viewer_plus':
      return access.highestRole !== null
    case 'org_member_plus':
      return (
        access.highestRole === Role.ORG_MEMBER || access.highestRole === Role.ORG_ADMIN
      )
    case 'org_admin_plus':
      return access.highestRole === Role.ORG_ADMIN
    case 'treasury':
      return access.hasTreasury
    case 'superadmin':
      return false // already handled by the isSuperadmin short-circuit above
    default:
      return false
  }
}

/** Whether the required permission is granted per-organisation (vs. app-wide). */
export function isOrgRelated(audience: DocAudience): boolean {
  return (
    audience === 'org_viewer_plus' ||
    audience === 'org_member_plus' ||
    audience === 'org_admin_plus' ||
    audience === 'treasury'
  )
}

/**
 * The organisations in which the user already meets the audience requirement.
 * Used to tell the user where they can perform the action. Empty for app-wide
 * audiences (`all`, `superadmin`).
 */
export function qualifyingOrgs(
  audience: DocAudience,
  memberships: MembershipWithOrganization[],
): OrgRef[] {
  const predicate = (m: MembershipWithOrganization): boolean => {
    switch (audience) {
      case 'org_viewer_plus':
        return true
      case 'org_member_plus':
        return m.role === Role.ORG_MEMBER || m.role === Role.ORG_ADMIN
      case 'org_admin_plus':
        return m.role === Role.ORG_ADMIN
      case 'treasury':
        return m.organization?.can_manage_payment_forms === true
      default:
        return false
    }
  }
  return memberships
    .filter(predicate)
    .map((m) => ({
      id: m.organization_id,
      name: m.organization?.name ?? 'Organisation',
    }))
}

/** French label for a scope badge. */
export function scopeLabel(scope: DocScope): string {
  switch (scope) {
    case 'application':
      return "Toute l'application"
    case 'organisation':
      return 'Organisation'
    case 'personne':
      return 'Personnel'
    default:
      return scope
  }
}

/** French label for an audience badge. */
export function audienceLabel(audience: DocAudience): string {
  switch (audience) {
    case 'all':
      return 'Tout le monde'
    case 'org_viewer_plus':
      return "Membres d'une organisation"
    case 'org_member_plus':
      return 'Éditeur.trice.s (rôle éditeur ou administrateur)'
    case 'org_admin_plus':
      return "Administrateurs d'organisation"
    case 'treasury':
      return 'Trésorerie'
    case 'superadmin':
      return 'Super-administrateurs'
    default:
      return audience
  }
}

/** Tailwind classes for a scope badge. */
export function scopeBadgeClass(scope: DocScope): string {
  switch (scope) {
    case 'application':
      return 'bg-blue-100 text-blue-800'
    case 'organisation':
      return 'bg-indigo-100 text-indigo-800'
    case 'personne':
      return 'bg-emerald-100 text-emerald-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
}

/** Tailwind classes for an audience badge. */
export function audienceBadgeClass(audience: DocAudience): string {
  switch (audience) {
    case 'all':
      return 'bg-gray-100 text-gray-700'
    case 'org_viewer_plus':
      return 'bg-green-100 text-green-800'
    case 'org_member_plus':
      return 'bg-amber-100 text-amber-800'
    case 'org_admin_plus':
      return 'bg-blue-100 text-blue-800'
    case 'treasury':
      return 'bg-teal-100 text-teal-800'
    case 'superadmin':
      return 'bg-purple-100 text-purple-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
}
