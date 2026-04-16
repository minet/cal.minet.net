import { httpClient } from './client'

export interface SecureKeyResponse {
  secure_key: string
}

export class CalendarApi {
  /** GET /calendar/securekey */
  async get_securekey(): Promise<string> {
    const res = await httpClient.get<string>('/calendar/securekey')
    return res.data
  }
}
