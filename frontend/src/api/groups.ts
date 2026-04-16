import { httpClient } from './client'
import type { GroupCreate, GroupRead, Message } from './types'

export interface GroupMemberRead {
  user_id: string
  membership_id: string
  email: string
  full_name: string | null
  profile_picture_url: string | null
  profile_picture_file: import('./types').StoredFileRead | null
}

export class GroupsApi {
  /** GET /organizations/{org_id}/groups */
  async get_organization_groups(orgId: string): Promise<GroupRead[]> {
    const res = await httpClient.get<GroupRead[]>(`/organizations/${orgId}/groups`)
    return res.data
  }

  /** POST /organizations/{org_id}/groups */
  async create_group(orgId: string, data: GroupCreate): Promise<GroupRead> {
    const res = await httpClient.post<GroupRead>(`/organizations/${orgId}/groups`, data)
    return res.data
  }

  /** DELETE /groups/{group_id} */
  async delete_group(groupId: string): Promise<Message> {
    const res = await httpClient.delete<Message>(`/groups/${groupId}`)
    return res.data
  }

  /** GET /groups/{group_id}/members */
  async get_group_members(groupId: string): Promise<GroupMemberRead[]> {
    const res = await httpClient.get<GroupMemberRead[]>(`/groups/${groupId}/members`)
    return res.data
  }

  /** POST /groups/{group_id}/members */
  async add_group_member(groupId: string, userEmail: string): Promise<Message> {
    const res = await httpClient.post<Message>(`/groups/${groupId}/members`, {
      user_email: userEmail,
    })
    return res.data
  }

  /** DELETE /groups/{group_id}/members/{user_id} */
  async remove_group_member(groupId: string, userId: string): Promise<Message> {
    const res = await httpClient.delete<Message>(`/groups/${groupId}/members/${userId}`)
    return res.data
  }

  /** DELETE /groups/{group_id}/members/me */
  async leave_group(groupId: string): Promise<Message> {
    const res = await httpClient.delete<Message>(`/groups/${groupId}/members/me`)
    return res.data
  }
}
