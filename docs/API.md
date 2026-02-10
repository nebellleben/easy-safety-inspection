# API Documentation

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

Most endpoints require authentication via JWT token. Include the token in the Authorization header:

```
Authorization: Bearer <access_token>
```

## Endpoints

### Authentication

#### POST /auth/login
Login with staff ID and password (admin users only).

**Request Body:**
```json
{
  "staff_id": "ADMIN001",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "full_name": "Admin User",
    "staff_id": "ADMIN001",
    "role": "super_admin",
    ...
  }
}
```

#### GET /auth/me
Get current authenticated user info.

**Response:** `User` object

#### POST /auth/logout
Logout (client-side token deletion).

---

### Findings

#### GET /findings
List findings with filtering.

**Query Parameters:**
- `area_id` (UUID, optional): Filter by area
- `severity` (string, optional): Filter by severity (low, medium, high, critical)
- `status` (string, optional): Filter by status (open, in_progress, resolved, closed)
- `date_from` (datetime, optional): Filter by date range start
- `date_to` (datetime, optional): Filter by date range end
- `page` (integer, default: 1): Page number
- `page_size` (integer, default: 50): Items per page

**Response:**
```json
{
  "items": [Finding],
  "total": 100,
  "page": 1,
  "page_size": 50,
  "total_pages": 2
}
```

#### GET /findings/{id}
Get finding details by ID.

**Response:** `Finding` object

#### PATCH /findings/{id}/status
Update finding status (admin only).

**Request Body:**
```json
{
  "status": "in_progress",
  "notes": "Started investigation"
}
```

**Response:** Updated `Finding` object

#### PATCH /findings/{id}/assign
Assign finding to a user (admin only).

**Query Parameters:**
- `assigned_to` (UUID, optional): User ID to assign to, or null to unassign

**Response:** Updated `Finding` object

#### POST /findings/summary
Generate summary report (admin only).

**Query Parameters:**
- `date_from` (datetime, required): Report start date
- `date_to` (datetime, optional): Report end date

**Response:** Summary statistics

---

### Areas

#### GET /areas
List areas with optional filtering.

**Query Parameters:**
- `level` (integer, optional): Filter by hierarchy level (1, 2, 3)
- `parent_id` (UUID, optional): Filter by parent area

**Response:** Array of `Area` objects

#### GET /areas/tree
Get areas as a tree structure.

**Response:** Array of `Area` objects with nested children

#### GET /areas/{id}
Get area details by ID.

**Response:** `Area` object

#### POST /areas
Create a new area (super-admin only).

**Request Body:**
```json
{
  "name": "Production",
  "description": "Production department",
  "parent_id": null,
  "level": 1
}
```

**Response:** Created `Area` object

#### PATCH /areas/{id}
Update an area (super-admin only).

**Response:** Updated `Area` object

#### DELETE /areas/{id}
Delete an area (super-admin only).

---

### Users (Admin)

#### GET /admin/users
List all users (super-admin only).

**Query Parameters:**
- `role` (string, optional): Filter by role
- `is_active` (boolean, optional): Filter by active status
- `page` (integer, default: 1)
- `page_size` (integer, default: 100)

**Response:** Array of `User` objects

#### GET /admin/users/{id}
Get user details (super-admin only).

**Response:** `User` object

#### POST /admin/users
Create a new user (super-admin only).

**Request Body:**
```json
{
  "full_name": "John Doe",
  "staff_id": "STF001",
  "department": "Production",
  "section": "Line A",
  "role": "admin",
  "password": "password123"
}
```

**Response:** Created `User` object

#### PATCH /admin/users/{id}
Update a user (super-admin only).

**Response:** Updated `User` object

#### DELETE /admin/users/{id}
Deactivate a user (super-admin only).

#### POST /admin/users/{id}/activate
Reactivate a deactivated user (super-admin only).

---

### Notifications

#### GET /notifications/settings
Get user's notification preferences.

**Response:**
```json
{
  "new_finding": true,
  "status_change": true,
  "daily_summary": true,
  "weekly_summary": true,
  "daily_summary_time": "09:00"
}
```

#### PATCH /notifications/settings
Update user's notification preferences.

**Response:** Updated `NotificationSettings` object

#### POST /notifications/test
Send a test notification to the user's Telegram.

---

## Data Models

### User
```typescript
{
  id: string
  telegram_id: number | null
  username: string | null
  full_name: string
  staff_id: string
  department: string
  section: string
  role: 'reporter' | 'admin' | 'super_admin'
  is_active: boolean
  created_at: string
  updated_at: string
}
```

### Area
```typescript
{
  id: string
  name: string
  description: string | null
  parent_id: string | null
  level: number
  created_at: string
  full_path: string | null
  children: Area[]
}
```

### Finding
```typescript
{
  id: string
  report_id: string
  reporter_id: string
  area_id: string
  description: string
  severity: 'low' | 'medium' | 'high' | 'critical'
  status: 'open' | 'in_progress' | 'resolved' | 'closed'
  location: string | null
  reported_at: string
  closed_at: string | null
  assigned_to: string | null
  created_at: string
  updated_at: string
  reporter: User
  assignee: User | null
  area: Area
  photos: Photo[]
  status_history: StatusHistory[]
}
```

### Photo
```typescript
{
  id: string
  finding_id: string
  s3_key: string
  original_filename: string
  mime_type: string
  size: number
  uploaded_at: string
}
```

### StatusHistory
```typescript
{
  id: string
  finding_id: string
  old_status: string | null
  new_status: string
  notes: string | null
  updated_by: string
  updated_at: string
}
```

---

## Error Responses

All errors follow this format:

```json
{
  "detail": "Error message description"
}
```

Common HTTP status codes:
- `400` Bad Request - Invalid input
- `401` Unauthorized - Invalid or missing authentication
- `403` Forbidden - Insufficient permissions
- `404` Not Found - Resource not found
- `422` Unprocessable Entity - Validation error
- `500` Internal Server Error - Server error
