import { httpClient } from './client'
import type { Message, PushTokenCreate, VapidKeyRead } from './types'

export class NotificationsApi {
  /** GET /notifications/vapid-public-key */
  async get_vapid_public_key(): Promise<VapidKeyRead> {
    const res = await httpClient.get<VapidKeyRead>('/notifications/vapid-public-key')
    return res.data
  }

  /** POST /notifications/subscribe */
  async subscribe_push(data: PushTokenCreate): Promise<Message> {
    const res = await httpClient.post<Message>('/notifications/subscribe', data)
    return res.data
  }

  /** DELETE /notifications/unsubscribe */
  async unsubscribe_push(endpoint: string): Promise<Message> {
    const res = await httpClient.delete<Message>('/notifications/unsubscribe', {
      params: { endpoint },
    })
    return res.data
  }
}
