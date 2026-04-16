import { httpClient } from './client'
import type { Message, ShortLinkCreate, ShortLinkInfo, ShortLinkRead } from './types'

export class ShortLinksApi {
  /** POST /short-links/ */
  async create_short_link(data: ShortLinkCreate): Promise<ShortLinkRead> {
    const res = await httpClient.post<ShortLinkRead>('/short-links/', data)
    return res.data
  }

  /** GET /short-links/info/{short_id} */
  async get_short_link_info(shortId: string): Promise<ShortLinkInfo> {
    const res = await httpClient.get<ShortLinkInfo>(`/short-links/info/${shortId}`)
    return res.data
  }

  /** POST /short-links/confirm/{short_id} */
  async confirm_short_link(shortId: string): Promise<Message> {
    const res = await httpClient.post<Message>(`/short-links/confirm/${shortId}`)
    return res.data
  }
}
