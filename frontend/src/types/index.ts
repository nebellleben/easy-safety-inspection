export type Role = 'reporter' | 'admin' | 'super_admin'

export type Severity = 'low' | 'medium' | 'high' | 'critical'

export type Status = 'open' | 'in_progress' | 'resolved' | 'closed'

export interface User {
  id: string
  telegram_id: number | null
  username: string | null
  full_name: string
  staff_id: string
  department: string
  section: string
  role: Role
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface Area {
  id: string
  name: string
  description: string | null
  parent_id: string | null
  level: number
  created_at: string
  full_path: string | null
  children: Area[]
}

export interface Photo {
  id: string
  finding_id: string
  s3_key: string
  original_filename: string
  mime_type: string
  size: number
  uploaded_at: string
}

export interface StatusHistory {
  id: string
  finding_id: string
  old_status: string | null
  new_status: string
  notes: string | null
  updated_by: string
  updated_at: string
}

export interface Finding {
  id: string
  report_id: string
  reporter_id: string
  area_id: string
  description: string
  severity: Severity
  status: Status
  location: string | null
  reported_at: string
  closed_at: string | null
  assigned_to: string | null
  created_at: string
  updated_at: string
  reporter?: User
  assignee?: User
  area?: Area
  photos?: Photo[]
  status_history?: StatusHistory[]
}

export interface FindingListResponse {
  items: Finding[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface LoginRequest {
  staff_id: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  user: User
}

export interface FindingStatusUpdate {
  status: Status
  notes?: string
}

export interface NotificationSettings {
  new_finding: boolean
  status_change: boolean
  daily_summary: boolean
  weekly_summary: boolean
  daily_summary_time: string
}
