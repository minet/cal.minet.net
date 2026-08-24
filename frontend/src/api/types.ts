// ============================================================
// Enums — mirror backend models.py
// ============================================================

export enum EventVisibility {
  DRAFT = "draft",
  PRIVATE = "private",
  PUBLIC_PENDING = "public_pending",
  PUBLIC_REJECTED = "public_rejected",
  PUBLIC_APPROVED = "public_approved",
}

export enum OrganizationType {
  ASSOCIATION = "association",
  CLUB = "club",
  LISTE = "liste",
  ADMINISTRATION = "administration",
  GATE = "gate",
}

export enum Role {
  ORG_ADMIN = "org_admin",
  ORG_MEMBER = "org_member",
  ORG_VIEWER = "org_viewer",
}

export enum PaymentFormStatus {
  PENDING = "pending",
  APPROVED = "approved",
  REJECTED = "rejected",
}

export enum PaymentType {
  HELLOASSO = "helloasso",
  CREDIT_CARD = "credit_card",
  CASH = "cash",
  CHEQUE = "cheque",
  EXCHANGE = "exchange",
  NONE = "none",
  OTHER = "other",
}

export enum ShortLinkType {
  EVENT = "EVENT",
  ORGANIZATION = "ORGANIZATION",
  TAG = "TAG",
}

export enum ShortLinkActionType {
  VIEW = "VIEW",
  SUBSCRIBE = "SUBSCRIBE",
  COUNTDOWN = "COUNTDOWN",
  PAYMENT = "PAYMENT",
}

// ============================================================
// Shared / base types
// ============================================================

export interface Message {
  message: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

// ============================================================
// Stored files
// ============================================================

export interface StoredFileVariantRead {
  width: number;
  url: string;
  format: string;
  size: number;
}

export interface StoredFileRead {
  id: string;
  url: string;
  variants: StoredFileVariantRead[];
  processed: boolean;
  file_type: string;
}

// ============================================================
// Tags
// ============================================================

export interface TagRead {
  id: string;
  name: string;
  color: string;
  organization_id: string;
  is_auto_approved: boolean | null;
}

export interface TagCreate {
  name: string;
  color: string;
}

export interface TagUpdate {
  name?: string;
  color?: string;
}

// ============================================================
// Organization links
// ============================================================

export interface OrganizationLinkRead {
  id: string;
  name: string;
  url: string;
  order: number;
}

export interface OrganizationLinkCreate {
  name: string;
  url: string;
  order?: number;
}

export interface OrganizationLinkUpdate {
  name?: string;
  url?: string;
  order?: number;
}

// ============================================================
// Organization images
// ============================================================

export interface OrganizationImageRead {
  id: string;
  url: string | null;
  filename: string;
  created_at: string;
  stored_file: StoredFileRead | null;
}

// ============================================================
// Organizations
// ============================================================

export interface OrganizationRead {
  id: string;
  name: string;
  logo_url: string | null;
  type: OrganizationType | null;
  slug: string | null;
  description: string | null;
  parent_id: string | null;
  delete_after: string | null;
  color_primary: string | null;
  color_secondary: string | null;
  color_dark: string | null;
  created_at: string | null;
  updated_at: string | null;
  organization_links: OrganizationLinkRead[];
  logo_file: StoredFileRead | null;
  can_edit: boolean | null;
  can_manage_payment_forms: boolean | null;
}

export interface OrganizationCreate {
  name: string;
  slug?: string;
  description?: string;
  type?: OrganizationType;
  parent_id?: string;
  color_primary?: string;
  color_secondary?: string;
  color_dark?: string;
  logo_file_id?: string;
}

// ============================================================
// Users
// ============================================================

export interface UserLinkRead {
  id: string;
  name: string;
  url: string;
  order: number;
}

export interface UserLinkCreate {
  name: string;
  url: string;
  order?: number;
}

export interface UserPublicRead {
  id: string;
  full_name: string | null;
  profile_picture_url: string | null;
  phone_number: string | null;
  links: UserLinkRead[];
  profile_picture_file: StoredFileRead | null;
}

export interface UserRead {
  id: string;
  email: string;
  full_name: string | null;
  profile_picture_url: string | null;
  phone_number: string | null;
  is_superadmin: boolean;
  exempt_from_rgpd_delete: boolean;
  is_active: boolean;
  notification_delay: number;
  last_seen_changelog_id: string | null;
  links: UserLinkRead[];
  profile_picture_file: StoredFileRead | null;
}

/** Extended UserRead returned by GET /auth/me */
export interface UserMeRead extends UserRead {
  pending_approvals_count: number;
  rejected_events_count: number;
}

export interface UserUpdate {
  full_name?: string;
  profile_picture_file_id?: string;
  phone_number?: string;
  notification_delay?: number;
}

export interface UserSearchResult {
  id: string;
  email: string;
  full_name: string | null;
}

export interface MembershipWithOrganization {
  id: string;
  user_id: string;
  organization_id: string;
  role: Role;
  title: string | null;
  organization: OrganizationRead | null;
}

export interface UserGroupRead {
  id: string;
  name: string;
  description: string | null;
  organization: { id: string; name: string };
  membership_id: string;
  joined_at: string;
}

// ============================================================
// Groups
// ============================================================

export interface GroupRead {
  id: string;
  name: string;
  description?: string | null;
  member_count?: number;
  created_at?: string;
}

export interface GroupCreate {
  name: string;
  description?: string;
}

// ============================================================
// Events
// ============================================================

export interface EventLinkRead {
  id: string;
  name: string;
  url: string;
  order: number;
}

export interface EventLinkCreate {
  name: string;
  url: string;
}

export interface ReactionSummary {
  emoji: string;
  count: number;
  user_reacted: boolean;
}

export interface ReactionDetail {
  user: UserPublicRead;
  emoji: string;
  created_at: string;
}

export interface EventRead {
  id: string;
  title: string;
  description: string | null;
  start_time: string;
  end_time: string;
  location: string | null;
  location_url: string | null;
  visibility: EventVisibility;
  hide_details: boolean;
  poster_url: string | null;
  video_url: string | null;
  rejection_message: string | null;
  approved_at: string | null;
  submitted_at: string | null;
  created_at: string;
  featured: number;
  is_featured: boolean;
  organization: OrganizationRead | null;
  guest_organizations: OrganizationRead[];
  tags: TagRead[];
  event_links: EventLinkRead[];
  group: GroupRead | null;
  created_by: UserPublicRead | null;
  created_by_id: string | null;
  reactions: ReactionSummary[];
  is_draft: boolean | null;
  poster_file: StoredFileRead | null;
  video_file: StoredFileRead | null;
}

export interface CreateEvent {
  title: string;
  description?: string;
  start_time: string;
  end_time: string;
  location?: string;
  location_url?: string;
  organization_id: string;
  visibility?: string;
  group_id?: string;
  tag_ids?: string[];
  guest_organization_ids?: string[];
  hide_details?: boolean;
  poster_file_id?: string;
  video_file_id?: string;
  links?: EventLinkCreate[];
}

export interface UpdateEvent {
  title?: string;
  description?: string;
  start_time?: string;
  end_time?: string;
  location?: string;
  location_url?: string;
  visibility?: string;
  group_id?: string;
  tag_ids?: string[];
  guest_organization_ids?: string[];
  poster_file_id?: string;
  video_file_id?: string;
  hide_details?: boolean;
  featured?: number;
  links?: EventLinkCreate[];
}

export interface RejectEventRequest {
  message: string;
}

export interface EventListParams {
  page?: number;
  size?: number;
  limit?: number;
  visibility?: EventVisibility | EventVisibility[];
  organization_id?: string;
  tag_ids?: string[];
  group_id?: string;
  featured?: boolean;
  upcoming_only?: boolean;
  upcoming?: boolean;
  search?: string;
  start_date?: string;
  end_date?: string;
}

export interface OverlappingCheckParams {
  start_time: string;
  end_time: string;
  organization_id?: string;
  exclude_event_id?: string;
}

// ============================================================
// Organization members
// ============================================================

export interface OrgMember {
  id: string;
  user_id: string;
  email: string;
  full_name: string | null;
  profile_picture_url: string | null;
  profile_picture_file: StoredFileRead | null;
  phone_number: string | null;
  role: Role;
  title: string | null;
  order: number;
  can_manage_payment_forms: boolean;
  hidden_from_years: number[];
  links: UserLinkRead[];
}

export interface MemberVisibilitySettings {
  hidden_from_years: number[];
}

// ============================================================
// Subscriptions
// ============================================================

export interface SubscriptionOrgEntry {
  id: string;
  organization: { id: string; name: string; logo_url: string | null };
}

export interface SubscriptionTagOrg {
  id: string;
  name: string;
  logo_url: string | null;
}

export interface SubscriptionTagEntry {
  id: string;
  tag: {
    id: string;
    name: string;
    color: string;
    organization: SubscriptionTagOrg | null;
  };
}

export interface SubscriptionsRead {
  subscribe_all: boolean;
  organizations: SubscriptionOrgEntry[];
  tags: SubscriptionTagEntry[];
}

// ============================================================
// Notifications / push
// ============================================================

export interface VapidKeyRead {
  public_key: string;
}

export interface PushTokenCreate {
  endpoint: string;
  keys: string;
}

// ============================================================
// Upload
// ============================================================

export interface UploadResponse {
  url: string;
  filename: string;
  stored_file_id: string;
}

// ============================================================
// HelloAsso
// ============================================================

export interface HelloAssoStatus {
  connected: boolean;
  helloasso_slug: string | null;
  api_client_id: string | null;
  can_manage_payment_forms: boolean;
}

export interface HelloAssoCredentialsDeleteResponse extends Message {
  forms_closed: number;
}

export interface HelloAssoCredentials {
  helloasso_slug: string;
  api_client_id: string;
  api_client_secret: string;
}

export interface HelloAssoFormSummary {
  form_type: string;
  form_slug: string;
  title: string;
  state: string;
  start_date: string | null;
  end_date: string | null;
}

export interface PaymentFormOption {
  id?: string;
  name: string;
  price_cents: number;
  is_private?: boolean;
  allowed_user_ids?: string[];
}

export interface PaymentFormCreate {
  total_amount_cents: number;
  item_name: string;
  options?: PaymentFormOption[];
}

export interface PaymentFormUpdate {
  item_name?: string;
  total_amount_cents?: number;
  options?: PaymentFormOption[];
  is_open?: boolean;
}

export interface BilleterieRead {
  id: string;
  helloasso_org_id: string;
  helloasso_form_slug: string;
  helloasso_form_title: string;
  helloasso_form_type: string;
  last_imported_at: string | null;
  created_at: string;
}

export interface PaymentFormRead {
  id: string;
  event_id: string;
  requesting_org_id: string;
  approving_org_id: string | null;
  total_amount_cents: number;
  item_name: string;
  status: PaymentFormStatus;
  options: PaymentFormOption[];
  is_open: boolean;
  rejection_message: string | null;
  payment_completed: boolean;
  entry_count: number;
  completed_count: number;
  created_by_id: string;
  reviewed_by_id: string | null;
  created_at: string;
  reviewed_at: string | null;
  billeterie: BilleterieRead | null;
}

export interface PaymentFormReject {
  rejection_message: string;
}

export interface ImportedOption {
  name: string;
  amount_cents: number;
}

export interface PaymentEntryRead {
  id: string;
  user_id: string | null;
  user_name: string | null;
  attendee_name: string | null;
  checkout_intent_id: string | null;
  helloasso_payment_id: string | null;
  helloasso_order_id: string | null;
  amount_cents: number;
  payment_type: string;
  selected_option_ids: string[];
  imported_options: ImportedOption[];
  completed: boolean;
  completed_at: string | null;
  cancelled: boolean;
  cancelled_at: string | null;
  created_at: string;
}

export interface PaymentDashboardItem {
  id: string;
  event_id: string;
  event_title: string;
  event_start_time: string;
  org_id: string;
  org_name: string;
  approving_org_id: string | null;
  item_name: string;
  total_amount_cents: number;
  options: PaymentFormOption[];
  status: PaymentFormStatus;
  is_open: boolean;
  entry_count: number;
  completed_count: number;
  baseline_total_amount_cents: number;
  baseline_participant_count: number;
  created_at: string;
  billeterie: BilleterieRead | null;
}

export interface MyPaymentEntryRead {
  id: string;
  event_id: string;
  event_title: string;
  event_start_time: string;
  org_name: string;
  item_name: string;
  amount_cents: number;
  payment_type: string;
  selected_options: PaymentFormOption[];
  completed: boolean;
  created_at: string;
}

export interface ValidationEntryRead {
  id: string;
  user_name: string | null;
  user_email: string | null;
  attendee_name: string | null;
  display_name: string;
  item_name: string;
  amount_cents: number;
  payment_type: string;
  selected_options: PaymentFormOption[];
  imported_options: ImportedOption[];
  completed: boolean;
  validated: boolean;
  validated_at: string | null;
  cancelled: boolean;
  created_at: string;
}

export interface PaymentInitiateRequest {
  selected_option_ids?: string[];
}

export interface PaymentInitiateResponse {
  redirect_url: string;
  checkout_intent_id: string;
}

export interface PaymentCheckResult {
  checked: number;
  completed: number;
  backfilled: number;
}

export interface ManualEntryCreate {
  attendee_name: string;
  payment_type?: PaymentType;
  amount_cents?: number;
  selected_option_ids?: string[];
  note?: string;
}

export interface AttendeeSearchResult {
  id: string | null;
  full_name: string | null;
  email: string | null;
  uid: string | null;
  source: string;
}

export interface BulkResolveRequest {
  queries: string[];
}

export interface BulkResolveResult {
  query: string;
  user_id: string | null;
  full_name: string | null;
}

export interface UserBatchLookupRequest {
  ids: string[];
}

export interface BilleterieCreate {
  org_id: string;
  form_slug: string;
  form_type?: string;
  form_title: string;
}

export interface BilleterieImportResult {
  imported: number;
  skipped: number;
}

// ============================================================
// Admin
// ============================================================

export interface LDAPSyncRequest {
  username: string;
  password: string;
}

export interface LDAPUserRead {
  id: string;
  email: string;
  full_name: string | null;
  uid: string | null;
  student_year: number | null;
}

// ============================================================
// Short links
// ============================================================

export interface ShortLinkCreate {
  item_type: ShortLinkType;
  item_id: string;
  action_type: ShortLinkActionType;
}

export interface ShortLinkRead {
  id: string;
  url: string;
}

export interface ShortLinkInfo {
  id: string;
  title: string;
  description: string | null;
  item_type: ShortLinkType;
  item_id: string;
  logo_url: string | null;
  logo_file: StoredFileRead | null;
  color_primary: string | null;
  color_secondary: string | null;
  color_dark: string | null;
  tag_color: string | null;
}

// ============================================================
// Calendar
// ============================================================

export interface SecureKeyRead {
  secure_key: string;
}

// ============================================================
// Changelog
// ============================================================

export type ChangelogAudience =
  | 'all'
  | 'org_viewer_plus'
  | 'org_member_plus'
  | 'org_admin_plus'
  | 'treasury'

export interface ChangelogEntryRead {
  id: string;
  title: string;
  content: string;
  audience: ChangelogAudience;
  image_urls: string[] | null;
  created_at: string;
}

export interface ChangelogEntryCreate {
  title: string;
  content: string;
  audience: ChangelogAudience;
  image_urls?: string[];
}

export interface ChangelogEntryUpdate {
  title?: string;
  content?: string;
  audience?: ChangelogAudience;
  image_urls?: string[];
}
