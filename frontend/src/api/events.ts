import { httpClient } from './client'
import type {
  CreateEvent,
  EventListParams,
  EventRead,
  Message,
  OverlappingCheckParams,
  PaginatedResponse,
  ReactionDetail,
  RejectEventRequest,
  UpdateEvent,
} from './types'

export class EventsApi {
  /** POST /events/ */
  async create_event(data: CreateEvent): Promise<EventRead> {
    const res = await httpClient.post<EventRead>('/events/', data)
    return res.data
  }

  /** GET /events/ */
  async list_events(params?: EventListParams): Promise<PaginatedResponse<EventRead>> {
    const res = await httpClient.get<PaginatedResponse<EventRead>>('/events/', { params })
    return res.data
  }

  /** GET /events/export — returns an ODS blob */
  async export(params?: Record<string, unknown>): Promise<Blob> {
    const res = await httpClient.get('/events/export', {
      params,
      responseType: 'blob',
    })
    return res.data as Blob
  }

  /** GET /events/drafts */
  async get_drafts(): Promise<EventRead[]> {
    const res = await httpClient.get<EventRead[]>('/events/drafts')
    return res.data
  }

  /** GET /events/my-events */
  async get_my_events(): Promise<EventRead[]> {
    const res = await httpClient.get<EventRead[]>('/events/my-events')
    return res.data
  }

  /** GET /events/overlapping-check */
  async overlapping_check(params: OverlappingCheckParams): Promise<EventRead[]> {
    const res = await httpClient.get<EventRead[]>('/events/overlapping-check', { params })
    return res.data
  }

  /** GET /events/pending-approvals */
  async get_pending_approvals(): Promise<EventRead[]> {
    const res = await httpClient.get<EventRead[]>('/events/pending-approvals')
    return res.data
  }

  /** GET /events/processed-approvals */
  async get_processed_approvals(): Promise<EventRead[]> {
    const res = await httpClient.get<EventRead[]>('/events/processed-approvals')
    return res.data
  }

  /** GET /events/{event_id} */
  async get_event(eventId: string): Promise<EventRead> {
    const res = await httpClient.get<EventRead>(`/events/${eventId}`)
    return res.data
  }

  /** PUT /events/{event_id} */
  async update_event(eventId: string, data: UpdateEvent): Promise<EventRead> {
    const res = await httpClient.put<EventRead>(`/events/${eventId}`, data)
    return res.data
  }

  /** DELETE /events/{event_id} */
  async delete_event(eventId: string): Promise<Message> {
    const res = await httpClient.delete<Message>(`/events/${eventId}`)
    return res.data
  }

  /** POST /events/{event_id}/approve */
  async approve_event(eventId: string): Promise<Message> {
    const res = await httpClient.post<Message>(`/events/${eventId}/approve`)
    return res.data
  }

  /** POST /events/{event_id}/reject */
  async reject_event(eventId: string, data: RejectEventRequest): Promise<Message> {
    const res = await httpClient.post<Message>(`/events/${eventId}/reject`, data)
    return res.data
  }

  /** POST /events/{event_id}/reset-status */
  async reset_status(eventId: string): Promise<Message> {
    const res = await httpClient.post<Message>(`/events/${eventId}/reset-status`)
    return res.data
  }

  /** POST /events/{event_id}/react */
  async add_reaction(eventId: string, emoji: string): Promise<Message> {
    const res = await httpClient.post<Message>(`/events/${eventId}/react`, { emoji })
    return res.data
  }

  /** GET /events/{event_id}/reactions */
  async get_event_reactions(eventId: string): Promise<ReactionDetail[]> {
    const res = await httpClient.get<ReactionDetail[]>(`/events/${eventId}/reactions`)
    return res.data
  }

  /** DELETE /events/{event_id}/reactions/{user_id} */
  async delete_reaction(eventId: string, userId: string): Promise<Message> {
    const res = await httpClient.delete<Message>(`/events/${eventId}/reactions/${userId}`)
    return res.data
  }

  /** GET /events/{event_id}/overlapping */
  async get_overlapping(eventId: string): Promise<EventRead[]> {
    const res = await httpClient.get<EventRead[]>(`/events/${eventId}/overlapping`)
    return res.data
  }
}
