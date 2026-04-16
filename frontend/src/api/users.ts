import { httpClient } from './client'
import type {
  MembershipWithOrganization,
  Message,
  OrganizationRead,
  PaginatedResponse,
  Role,
  UserGroupRead,
  UserLinkCreate,
  UserLinkRead,
  UserMeRead,
  UserRead,
  UserSearchResult,
  UserUpdate,
} from './types'

export class UsersApi {
  /** GET /users/me — same shape as auth/me but via users router */
  async get_me(): Promise<UserMeRead> {
    const res = await httpClient.get<UserMeRead>('/users/me')
    return res.data
  }

  /** GET /users/me/organizations */
  async get_user_organizations(): Promise<OrganizationRead[]> {
    const res = await httpClient.get<OrganizationRead[]>('/users/me/organizations')
    return res.data
  }

  /** GET /users/me/memberships */
  async get_user_memberships(): Promise<MembershipWithOrganization[]> {
    const res = await httpClient.get<MembershipWithOrganization[]>('/users/me/memberships')
    return res.data
  }

  /** GET /users/me/groups */
  async get_user_groups(): Promise<UserGroupRead[]> {
    const res = await httpClient.get<UserGroupRead[]>('/users/me/groups')
    return res.data
  }

  /** GET /users/me/links */
  async list_my_links(): Promise<UserLinkRead[]> {
    const res = await httpClient.get<UserLinkRead[]>('/users/me/links')
    return res.data
  }

  /** POST /users/me/links */
  async create_my_link(data: UserLinkCreate): Promise<UserLinkRead> {
    const res = await httpClient.post<UserLinkRead>('/users/me/links', data)
    return res.data
  }

  /** PUT /users/me/links/{link_id} */
  async update_my_link(linkId: string, data: UserLinkCreate): Promise<UserLinkRead> {
    const res = await httpClient.put<UserLinkRead>(`/users/me/links/${linkId}`, data)
    return res.data
  }

  /** DELETE /users/me/links/{link_id} */
  async delete_my_link(linkId: string): Promise<{ ok: boolean }> {
    const res = await httpClient.delete<{ ok: boolean }>(`/users/me/links/${linkId}`)
    return res.data
  }

  /** PUT /users/me */
  async update_user_profile(data: UserUpdate): Promise<UserRead> {
    const res = await httpClient.put<UserRead>('/users/me', data)
    return res.data
  }

  /** GET /users/search */
  async search_users(q: string): Promise<UserSearchResult[]> {
    const res = await httpClient.get<UserSearchResult[]>('/users/search', { params: { q } })
    return res.data
  }

  /** GET /users/ (superadmin only) */
  async list_users(params?: {
    page?: number
    size?: number
    search?: string
  }): Promise<PaginatedResponse<UserRead>> {
    const res = await httpClient.get<PaginatedResponse<UserRead>>('/users/', { params })
    return res.data
  }

  /** GET /users/{user_id} */
  async get_user_profile(userId: string): Promise<UserRead> {
    const res = await httpClient.get<UserRead>(`/users/${userId}`)
    return res.data
  }

  /** GET /users/{user_id}/memberships */
  async get_other_user_memberships(userId: string): Promise<MembershipWithOrganization[]> {
    const res = await httpClient.get<MembershipWithOrganization[]>(
      `/users/${userId}/memberships`,
    )
    return res.data
  }

  /** GET /users/{user_id}/links */
  async list_user_links(userId: string): Promise<UserLinkRead[]> {
    const res = await httpClient.get<UserLinkRead[]>(`/users/${userId}/links`)
    return res.data
  }

  /** POST /users/invite */
  async invite_user(email: string): Promise<UserRead> {
    const res = await httpClient.post<UserRead>('/users/invite', { email })
    return res.data
  }

  /** PUT /users/{user_id}/superadmin */
  async toggle_superadmin(userId: string, isSuperadmin: boolean): Promise<UserRead> {
    const res = await httpClient.put<UserRead>(
      `/users/${userId}/superadmin`,
      null,
      { params: { is_superadmin: isSuperadmin } },
    )
    return res.data
  }

  /** PUT /users/{user_id}/exempt-ldap */
  async toggle_exempt_from_rgpd_delete(userId: string, exempt: boolean): Promise<UserRead> {
    const res = await httpClient.put<UserRead>(
      `/users/${userId}/exempt-ldap`,
      null,
      { params: { exempt } },
    )
    return res.data
  }

  /** PUT /users/{user_id}/active */
  async toggle_active(userId: string, isActive: boolean): Promise<UserRead> {
    const res = await httpClient.put<UserRead>(
      `/users/${userId}/active`,
      null,
      { params: { is_active: isActive } },
    )
    return res.data
  }

  /** DELETE /users/{user_id} */
  async delete_user(userId: string): Promise<{ ok: boolean }> {
    const res = await httpClient.delete<{ ok: boolean }>(`/users/${userId}`)
    return res.data
  }

  /** PUT /users/{user_id}/role — add to org (used from UserProfileView) */
  async add_to_organization(
    orgId: string,
    email: string,
    role: Role,
    title?: string,
  ): Promise<Message> {
    const res = await httpClient.post<Message>(`/organizations/${orgId}/members`, {
      email,
      role,
      title,
    })
    return res.data
  }
}
