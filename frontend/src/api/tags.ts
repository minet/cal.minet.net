import { httpClient } from './client'
import type { Message, TagCreate, TagRead, TagUpdate } from './types'

export class TagsApi {
  /** GET /organizations/{org_id}/tags */
  async get_organization_tags(orgId: string): Promise<TagRead[]> {
    const res = await httpClient.get<TagRead[]>(`/organizations/${orgId}/tags`)
    return res.data
  }

  /** POST /organizations/{org_id}/tags */
  async create_tag(orgId: string, data: TagCreate): Promise<TagRead> {
    const res = await httpClient.post<TagRead>(`/organizations/${orgId}/tags`, data)
    return res.data
  }

  /** PUT /tags/{tag_id} */
  async update_tag(tagId: string, data: TagUpdate): Promise<TagRead> {
    const res = await httpClient.put<TagRead>(`/tags/${tagId}`, data)
    return res.data
  }

  /** DELETE /tags/{tag_id} */
  async delete_tag(tagId: string): Promise<Message> {
    const res = await httpClient.delete<Message>(`/tags/${tagId}`)
    return res.data
  }

  /** PUT /tags/{tag_id}/auto-approve */
  async toggle_auto_approve(tagId: string, isAutoApproved: boolean): Promise<TagRead> {
    const res = await httpClient.put<TagRead>(
      `/tags/${tagId}/auto-approve`,
      null,
      { params: { is_auto_approved: isAutoApproved } },
    )
    return res.data
  }
}
