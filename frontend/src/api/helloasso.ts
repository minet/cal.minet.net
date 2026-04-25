import { httpClient } from './client'
import type {
  AttendeeSearchResult,
  BilleterieCreate,
  BilleterieImportResult,
  BilleterieRead,
  BulkResolveRequest,
  BulkResolveResult,
  HelloAssoCredentials,
  HelloAssoFormSummary,
  HelloAssoStatus,
  ManualEntryCreate,
  Message,
  MyPaymentEntryRead,
  PaymentCheckResult,
  PaymentDashboardItem,
  PaymentEntryRead,
  PaymentFormCreate,
  PaymentFormRead,
  PaymentFormReject,
  PaymentFormUpdate,
  PaymentInitiateRequest,
  PaymentInitiateResponse,
  UserBatchLookupRequest,
  ValidationEntryRead,
} from './types'

export class HelloAssoApi {
  // ------------------------------------------------------------------
  // Credentials
  // ------------------------------------------------------------------

  /** GET /helloasso/status/{org_id} */
  async helloasso_status(orgId: string): Promise<HelloAssoStatus> {
    const res = await httpClient.get<HelloAssoStatus>(`/helloasso/status/${orgId}`)
    return res.data
  }

  /** PUT /helloasso/credentials/{org_id} */
  async set_credentials(orgId: string, data: HelloAssoCredentials): Promise<HelloAssoStatus> {
    const res = await httpClient.put<HelloAssoStatus>(`/helloasso/credentials/${orgId}`, data)
    return res.data
  }

  /** DELETE /helloasso/credentials/{org_id} */
  async delete_credentials(orgId: string): Promise<Message> {
    const res = await httpClient.delete<Message>(`/helloasso/credentials/${orgId}`)
    return res.data
  }

  // ------------------------------------------------------------------
  // Payment forms (per-event)
  // ------------------------------------------------------------------

  /** POST /helloasso/events/{event_id}/payment-form */
  async create_payment_form(eventId: string, data: PaymentFormCreate): Promise<PaymentFormRead> {
    const res = await httpClient.post<PaymentFormRead>(
      `/helloasso/events/${eventId}/payment-form`,
      data,
    )
    return res.data
  }

  /** GET /helloasso/events/{event_id}/payment-form */
  async get_payment_form(eventId: string): Promise<PaymentFormRead> {
    const res = await httpClient.get<PaymentFormRead>(
      `/helloasso/events/${eventId}/payment-form`,
    )
    return res.data
  }

  /** PUT /helloasso/events/{event_id}/payment-form */
  async update_payment_form(
    eventId: string,
    data: PaymentFormUpdate,
  ): Promise<PaymentFormRead> {
    const res = await httpClient.put<PaymentFormRead>(
      `/helloasso/events/${eventId}/payment-form`,
      data,
    )
    return res.data
  }

  /** DELETE /helloasso/events/{event_id}/payment-form */
  async delete_payment_form(eventId: string): Promise<Message> {
    const res = await httpClient.delete<Message>(`/helloasso/events/${eventId}/payment-form`)
    return res.data
  }

  /** POST /helloasso/events/{event_id}/payment-form/approve */
  async approve_payment_form(eventId: string): Promise<PaymentFormRead> {
    const res = await httpClient.post<PaymentFormRead>(
      `/helloasso/events/${eventId}/payment-form/approve`,
    )
    return res.data
  }

  /** POST /helloasso/events/{event_id}/payment-form/reject */
  async reject_payment_form(
    eventId: string,
    data: PaymentFormReject,
  ): Promise<PaymentFormRead> {
    const res = await httpClient.post<PaymentFormRead>(
      `/helloasso/events/${eventId}/payment-form/reject`,
      data,
    )
    return res.data
  }

  // ------------------------------------------------------------------
  // Dashboard / listings
  // ------------------------------------------------------------------

  /** GET /helloasso/pending-forms/{org_id} */
  async get_pending_forms(orgId: string): Promise<PaymentFormRead[]> {
    const res = await httpClient.get<PaymentFormRead[]>(`/helloasso/pending-forms/${orgId}`)
    return res.data
  }

  /** GET /helloasso/my-payment-forms */
  async get_my_payment_forms(params?: {
    page?: number
    size?: number
    status?: string
    time_filter?: string
  }): Promise<PaymentDashboardItem[]> {
    const res = await httpClient.get<PaymentDashboardItem[]>('/helloasso/my-payment-forms', {
      params,
    })
    return res.data
  }

  /** GET /helloasso/my-entries */
  async get_my_entries(): Promise<MyPaymentEntryRead[]> {
    const res = await httpClient.get<MyPaymentEntryRead[]>('/helloasso/my-entries')
    return res.data
  }

  // ------------------------------------------------------------------
  // Payment entries (per-event)
  // ------------------------------------------------------------------

  /** GET /helloasso/events/{event_id}/payment-form/entries */
  async get_payment_entries(eventId: string): Promise<PaymentEntryRead[]> {
    const res = await httpClient.get<PaymentEntryRead[]>(
      `/helloasso/events/${eventId}/payment-form/entries`,
    )
    return res.data
  }

  /** GET /helloasso/events/{event_id}/payment-form/entries/export — ODS blob */
  async export_payment_entries(
    eventId: string,
    params?: Record<string, unknown>,
  ): Promise<Blob> {
    const res = await httpClient.get(
      `/helloasso/events/${eventId}/payment-form/entries/export`,
      { params, responseType: 'blob' },
    )
    return res.data as Blob
  }

  /** GET /helloasso/events/{event_id}/my-entry */
  async get_my_entry(eventId: string): Promise<MyPaymentEntryRead | null> {
    const res = await httpClient.get<MyPaymentEntryRead | null>(
      `/helloasso/events/${eventId}/my-entry`,
    )
    return res.data
  }

  // ------------------------------------------------------------------
  // Validation
  // ------------------------------------------------------------------

  /** GET /helloasso/events/{event_id}/validation-entries */
  async get_validation_entries(eventId: string): Promise<ValidationEntryRead[]> {
    const res = await httpClient.get<ValidationEntryRead[]>(
      `/helloasso/events/${eventId}/validation-entries`,
    )
    return res.data
  }

  /** POST /helloasso/entries/{entry_id}/validate */
  async validate_entry(entryId: string): Promise<ValidationEntryRead> {
    const res = await httpClient.post<ValidationEntryRead>(
      `/helloasso/entries/${entryId}/validate`,
    )
    return res.data
  }

  /** POST /helloasso/entries/{entry_id}/cancel */
  async cancel_entry(entryId: string): Promise<ValidationEntryRead> {
    const res = await httpClient.post<ValidationEntryRead>(
      `/helloasso/entries/${entryId}/cancel`,
    )
    return res.data
  }

  /** GET /helloasso/events/{event_id}/attendee-search */
  async search_attendees(eventId: string, q: string): Promise<AttendeeSearchResult[]> {
    const res = await httpClient.get<AttendeeSearchResult[]>(
      `/helloasso/events/${eventId}/attendee-search`,
      { params: { q } },
    )
    return res.data
  }

  /** POST /helloasso/events/{event_id}/attendee-bulk-resolve */
  async bulk_resolve_attendees(
    eventId: string,
    data: BulkResolveRequest,
  ): Promise<BulkResolveResult[]> {
    const res = await httpClient.post<BulkResolveResult[]>(
      `/helloasso/events/${eventId}/attendee-bulk-resolve`,
      data,
    )
    return res.data
  }

  /** POST /helloasso/events/{event_id}/manual-entry */
  async create_manual_entry(
    eventId: string,
    data: ManualEntryCreate,
  ): Promise<ValidationEntryRead> {
    const res = await httpClient.post<ValidationEntryRead>(
      `/helloasso/events/${eventId}/manual-entry`,
      data,
    )
    return res.data
  }

  // ------------------------------------------------------------------
  // Payment initiation (user-facing)
  // ------------------------------------------------------------------

  /** POST /helloasso/events/{event_id}/initiate-payment */
  async initiate_payment(
    eventId: string,
    data: PaymentInitiateRequest,
  ): Promise<PaymentInitiateResponse> {
    const res = await httpClient.post<PaymentInitiateResponse>(
      `/helloasso/events/${eventId}/initiate-payment`,
      data,
    )
    return res.data
  }

  /** POST /helloasso/events/{event_id}/check-payment-status */
  async check_payment_status(eventId: string): Promise<PaymentCheckResult> {
    const res = await httpClient.post<PaymentCheckResult>(
      `/helloasso/events/${eventId}/check-payment-status`,
    )
    return res.data
  }

  // ------------------------------------------------------------------
  // Billeterie
  // ------------------------------------------------------------------

  /** GET /helloasso/{org_id}/billeteries */
  async get_billeteries(orgId: string): Promise<HelloAssoFormSummary[]> {
    const res = await httpClient.get<HelloAssoFormSummary[]>(
      `/helloasso/${orgId}/billeteries`,
    )
    return res.data
  }

  /** POST /helloasso/events/{event_id}/payment-form/billeterie */
  async create_billeterie(eventId: string, data: BilleterieCreate): Promise<BilleterieRead> {
    const res = await httpClient.post<BilleterieRead>(
      `/helloasso/events/${eventId}/payment-form/billeterie`,
      data,
    )
    return res.data
  }

  /** DELETE /helloasso/events/{event_id}/payment-form/billeterie */
  async delete_billeterie(eventId: string): Promise<Message> {
    const res = await httpClient.delete<Message>(
      `/helloasso/events/${eventId}/payment-form/billeterie`,
    )
    return res.data
  }

  /** POST /helloasso/events/{event_id}/payment-form/billeterie/import */
  async import_billeterie(eventId: string): Promise<BilleterieImportResult> {
    const res = await httpClient.post<BilleterieImportResult>(
      `/helloasso/events/${eventId}/payment-form/billeterie/import`,
    )
    return res.data
  }

  // ------------------------------------------------------------------
  // Batch helpers
  // ------------------------------------------------------------------

  /** POST /helloasso/users/batch-lookup */
  async batch_lookup_users(data: UserBatchLookupRequest): Promise<AttendeeSearchResult[]> {
    const res = await httpClient.post<AttendeeSearchResult[]>(
      '/helloasso/users/batch-lookup',
      data,
    )
    return res.data
  }

  /** GET /helloasso/{org_id}/checkouts/export — ODS blob */
  async export_checkouts(orgId: string, params?: Record<string, unknown>): Promise<Blob> {
    const res = await httpClient.get(`/helloasso/${orgId}/checkouts/export`, {
      params,
      responseType: 'blob',
    })
    return res.data as Blob
  }
}
