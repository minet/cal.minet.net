import { httpClient } from './client'
import type { Message, SubscriptionsRead } from './types'

export class SubscriptionsApi {
  /** GET /subscriptions/me */
  async get_my_subscriptions(): Promise<SubscriptionsRead> {
    const res = await httpClient.get<SubscriptionsRead>('/subscriptions/me')
    return res.data
  }

  /** POST /subscriptions/organizations/{org_id} */
  async subscribe_to_organization(orgId: string): Promise<Message> {
    const res = await httpClient.post<Message>(`/subscriptions/organizations/${orgId}`)
    return res.data
  }

  /** DELETE /subscriptions/organizations/{org_id} */
  async unsubscribe_from_organization(orgId: string): Promise<Message> {
    const res = await httpClient.delete<Message>(`/subscriptions/organizations/${orgId}`)
    return res.data
  }

  /** POST /subscriptions/tags/{tag_id} */
  async subscribe_to_tag(tagId: string): Promise<Message> {
    const res = await httpClient.post<Message>(`/subscriptions/tags/${tagId}`)
    return res.data
  }

  /** DELETE /subscriptions/tags/{tag_id} */
  async unsubscribe_from_tag(tagId: string): Promise<Message> {
    const res = await httpClient.delete<Message>(`/subscriptions/tags/${tagId}`)
    return res.data
  }

  /** POST /subscriptions/all */
  async subscribe_to_all(): Promise<Message> {
    const res = await httpClient.post<Message>('/subscriptions/all')
    return res.data
  }

  /** DELETE /subscriptions/all */
  async unsubscribe_from_all(): Promise<Message> {
    const res = await httpClient.delete<Message>('/subscriptions/all')
    return res.data
  }
}
