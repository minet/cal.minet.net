import { httpClient } from './client'
import type { ChangelogEntryCreate, ChangelogEntryRead, ChangelogEntryUpdate } from './types'

export class ChangelogApi {
  /** GET /changelogs — all visible entries for current user, newest first */
  async list(): Promise<ChangelogEntryRead[]> {
    const res = await httpClient.get<ChangelogEntryRead[]>('/changelogs')
    return res.data
  }

  /** GET /changelogs/unseen — entries newer than last_seen, oldest first */
  async listUnseen(): Promise<ChangelogEntryRead[]> {
    const res = await httpClient.get<ChangelogEntryRead[]>('/changelogs/unseen')
    return res.data
  }

  /** POST /changelogs — superadmin only */
  async create(data: ChangelogEntryCreate): Promise<ChangelogEntryRead> {
    const res = await httpClient.post<ChangelogEntryRead>('/changelogs', data)
    return res.data
  }

  /** PUT /changelogs/{id} — superadmin only */
  async update(id: string, data: ChangelogEntryUpdate): Promise<ChangelogEntryRead> {
    const res = await httpClient.put<ChangelogEntryRead>(`/changelogs/${id}`, data)
    return res.data
  }

  /** DELETE /changelogs/{id} — superadmin only */
  async delete(id: string): Promise<void> {
    await httpClient.delete(`/changelogs/${id}`)
  }

  /** POST /changelogs/mark-seen/{id} */
  async markSeen(id: string): Promise<void> {
    await httpClient.post(`/changelogs/mark-seen/${id}`)
  }
}
