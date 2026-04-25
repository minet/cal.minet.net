/**
 * Typed API client — one class per FastAPI router.
 *
 * Usage:
 *   import { api } from '@/api'
 *   const events = await api.events.list_events()
 *   const org = await api.organizations.get_organization(id)
 */

import { AdminApi } from './admin'
import { AuthApi } from './auth'
import { CalendarApi } from './calendar'
import { ChangelogApi } from './changelogs'
import { EventsApi } from './events'
import { GroupsApi } from './groups'
import { HelloAssoApi } from './helloasso'
import { NotificationsApi } from './notifications'
import { OrganizationImagesApi } from './organization_images'
import { OrganizationLinksApi } from './organization_links'
import { OrganizationsApi } from './organizations'
import { ShortLinksApi } from './short_links'
import { SubscriptionsApi } from './subscriptions'
import { TagsApi } from './tags'
import { UploadApi } from './upload'
import { UsersApi } from './users'

class ApiClient {
  readonly auth = new AuthApi()
  readonly events = new EventsApi()
  readonly organizations = new OrganizationsApi()
  readonly users = new UsersApi()
  readonly tags = new TagsApi()
  readonly groups = new GroupsApi()
  readonly subscriptions = new SubscriptionsApi()
  readonly notifications = new NotificationsApi()
  readonly upload = new UploadApi()
  readonly helloasso = new HelloAssoApi()
  readonly admin = new AdminApi()
  readonly calendar = new CalendarApi()
  readonly short_links = new ShortLinksApi()
  readonly organization_links = new OrganizationLinksApi()
  readonly organization_images = new OrganizationImagesApi()
  readonly changelog = new ChangelogApi()
}

export const api = new ApiClient()

// Re-export types for convenience
export * from './types'
export * from './groups'
export { httpClient } from './client'
