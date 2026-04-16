import { httpClient } from './client'
import type { EventRead, Message, OrgMember, OrganizationCreate, OrganizationRead, Role } from './types'

export class OrganizationsApi {
  /** POST /organizations/ */
  async create_organization(data: OrganizationCreate): Promise<OrganizationRead> {
    const res = await httpClient.post<OrganizationRead>('/organizations/', data)
    return res.data
  }

  /** GET /organizations/ */
  async list_organizations(): Promise<OrganizationRead[]> {
    const res = await httpClient.get<OrganizationRead[]>('/organizations/')
    return res.data
  }

  /** GET /organizations/{org_id} */
  async get_organization(orgId: string): Promise<OrganizationRead> {
    const res = await httpClient.get<OrganizationRead>(`/organizations/${orgId}`)
    return res.data
  }

  /** PUT /organizations/{org_id} */
  async update_organization(
    orgId: string,
    data: Partial<OrganizationCreate>,
  ): Promise<OrganizationRead> {
    const res = await httpClient.put<OrganizationRead>(`/organizations/${orgId}`, data)
    return res.data
  }

  /** DELETE /organizations/{org_id} */
  async delete_organization(orgId: string): Promise<Message> {
    const res = await httpClient.delete<Message>(`/organizations/${orgId}`)
    return res.data
  }

  /** GET /organizations/{org_id}/members */
  async get_organization_members(orgId: string): Promise<OrgMember[]> {
    const res = await httpClient.get<OrgMember[]>(`/organizations/${orgId}/members`)
    return res.data
  }

  /** POST /organizations/{org_id}/members/reorder */
  async reorder_organization_members(orgId: string, membershipIds: string[]): Promise<Message> {
    const res = await httpClient.post<Message>(`/organizations/${orgId}/members/reorder`, {
      membership_ids: membershipIds,
    })
    return res.data
  }

  /** POST /organizations/{org_id}/members */
  async add_organization_member(
    orgId: string,
    email: string,
    role: Role,
    title?: string,
  ): Promise<{ message: string; membership_id: string }> {
    const res = await httpClient.post<{ message: string; membership_id: string }>(
      `/organizations/${orgId}/members`,
      { email, role, title },
    )
    return res.data
  }

  /** PUT /organizations/{org_id}/members/{membership_id} */
  async update_member_role(
    orgId: string,
    membershipId: string,
    params: { role?: Role; title?: string; can_manage_payment_forms?: boolean },
  ): Promise<Message> {
    const res = await httpClient.put<Message>(
      `/organizations/${orgId}/members/${membershipId}`,
      null,
      { params },
    )
    return res.data
  }

  /** DELETE /organizations/{org_id}/members/{membership_id} */
  async remove_organization_member(orgId: string, membershipId: string): Promise<Message> {
    const res = await httpClient.delete<Message>(
      `/organizations/${orgId}/members/${membershipId}`,
    )
    return res.data
  }

  /** GET /organizations/{org_id}/events */
  async get_organization_events(orgId: string): Promise<EventRead[]> {
    const res = await httpClient.get<EventRead[]>(`/organizations/${orgId}/events`)
    return res.data
  }

  /** GET /organizations/{org_id}/can-edit */
  async can_edit_organization(orgId: string): Promise<{ can_edit: boolean; reason: string }> {
    const res = await httpClient.get<{ can_edit: boolean; reason: string }>(
      `/organizations/${orgId}/can-edit`,
    )
    return res.data
  }
}
