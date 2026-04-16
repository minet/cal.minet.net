import { httpClient } from './client'
import type { Message, OrganizationLinkCreate, OrganizationLinkRead, OrganizationLinkUpdate } from './types'

export class OrganizationLinksApi {
  /** GET /organizations/{org_id}/links */
  async get_organization_links(orgId: string): Promise<OrganizationLinkRead[]> {
    const res = await httpClient.get<OrganizationLinkRead[]>(`/organizations/${orgId}/links`)
    return res.data
  }

  /** POST /organizations/{org_id}/links */
  async create_organization_link(
    orgId: string,
    data: OrganizationLinkCreate,
  ): Promise<OrganizationLinkRead> {
    const res = await httpClient.post<OrganizationLinkRead>(
      `/organizations/${orgId}/links`,
      data,
    )
    return res.data
  }

  /** PUT /organization-links/{link_id} */
  async update_organization_link(
    linkId: string,
    data: OrganizationLinkUpdate,
  ): Promise<OrganizationLinkRead> {
    const res = await httpClient.put<OrganizationLinkRead>(
      `/organization-links/${linkId}`,
      data,
    )
    return res.data
  }

  /** DELETE /organization-links/{link_id} */
  async delete_organization_link(linkId: string): Promise<Message> {
    const res = await httpClient.delete<Message>(`/organization-links/${linkId}`)
    return res.data
  }
}
