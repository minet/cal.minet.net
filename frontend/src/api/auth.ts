import { httpClient } from './client'
import type { UserMeRead } from './types'

export class AuthApi {
  /** GET /auth/me — full user profile with stats */
  async read_users_me(): Promise<UserMeRead> {
    const res = await httpClient.get<UserMeRead>('/auth/me')
    return res.data
  }

  /** PUT /auth/me — update facebook_link / phone_number */
  async update_user_profile(params: {
    facebook_link?: string
    phone_number?: string
  }): Promise<UserMeRead> {
    const res = await httpClient.put<UserMeRead>('/auth/me', null, { params })
    return res.data
  }
}
