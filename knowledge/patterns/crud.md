# CRUD — Product Pattern

## Common Pages
- **List** — table/card view of all records with search, filter, sort, pagination
- **Create** — form to add a new record
- **Edit** — form (pre-filled) to update existing record
- **Show/Detail** — read-only view of a single record
- **Delete** — confirmation dialog (soft or hard delete)

## Common Entities
- id (UUID or auto-increment)
- created_at, updated_at timestamps
- is_active / status field for soft deletes
- created_by / owner reference

## Common Workflows
1. User opens list page → sees all records with pagination
2. User clicks "Create" → fills form → submits → returns to list
3. User clicks a record → navigates to detail/edit view
4. User edits fields → saves → list reflects changes
5. User deletes record → confirms → record removed or soft-deleted

## Common API Endpoints
| Method | Path | Action |
|--------|------|--------|
| GET | /api/{resource} | List with pagination, filtering, sorting |
| GET | /api/{resource}/:id | Get single record |
| POST | /api/{resource} | Create record |
| PUT/PATCH | /api/{resource}/:id | Update record |
| DELETE | /api/{resource}/:id | Delete record |
| POST | /api/{resource}/bulk | Batch operations |

## Common UI Components
- **Table/TanStack Table** — sortable columns, row selection, pagination controls
- **Search bar** — text search across fields
- **Filter panel** — dropdowns, date range, multi-select
- **Create/Edit form** — field-by-field layout with validation
- **Detail card** — read-only field display
- **Delete dialog** — confirmation with reason field
- **Pagination** — page numbers + page size selector
- **Batch action bar** — select all, delete selected, export selected

## Common Dashboards
- Record count over time (line chart)
- Recent activity feed
- CRUD usage metrics (creates vs edits vs deletes per day)

## Common Reports
- Full data export (CSV/Excel)
- Audit log of changes
- Daily change summary
