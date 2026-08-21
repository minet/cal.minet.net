import { httpClient } from './client'
import type { LDAPSyncRequest, LDAPUserRead, Message, UserRead } from './types'

export class AdminApi {
  /** POST /admin/ldap/sync */
  async sync_ldap_users(data: LDAPSyncRequest): Promise<Message> {
    const res = await httpClient.post<Message>('/admin/ldap/sync', data)
    return res.data
  }

  /** GET /admin/ldap/users */
  async search_ldap_users(q?: string): Promise<LDAPUserRead[]> {
    const res = await httpClient.get<LDAPUserRead[]>('/admin/ldap/users', {
      params: q ? { q } : undefined,
    })
    return res.data
  }

  /** GET /admin/ldap/orphans */
  async get_ldap_orphaned_users(): Promise<UserRead[]> {
    const res = await httpClient.get<UserRead[]>('/admin/ldap/orphans')
    return res.data
  }

  /** POST /admin/housekeeping */
  async housekeeping(deleteOrphanUsers?: boolean): Promise<Message> {
    const res = await httpClient.post<Message>('/admin/housekeeping', null, {
      params: deleteOrphanUsers !== undefined
        ? { delete_orphan_users: deleteOrphanUsers }
        : undefined,
    })
    return res.data
  }

  /** POST /admin/mandate-reminders/send */
  async send_mandate_reminders(): Promise<{ message: string; count: number }> {
    const res = await httpClient.post<{ message: string; count: number }>(
      '/admin/mandate-reminders/send',
    )
    return res.data
  }
}
