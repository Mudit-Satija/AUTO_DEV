# CRM — Product Pattern

## Common Pages
- **Dashboard** — pipeline value, deals by stage, recent activity
- **Contacts** — list of contacts with search, filter, tags
- **Contact Detail** — profile with activity history, notes, deals
- **Companies/Accounts** — organization list with hierarchy
- **Company Detail** — company profile, contacts, deals, activity
- **Deals/Pipeline** — kanban or table view by stage
- **Deal Detail** — amount, stage, contacts, notes, activities
- **Activities** — calls, emails, meetings with reminders
- **Email Inbox** — synced email with templates and tracking
- **Reports** — pipeline analytics, conversion, team performance
- **Settings** — pipelines, stages, custom fields, roles

## Common Entities
- Contact (name, email, phone, company, title, tags, owner)
- Company (name, industry, size, website, address, owner)
- Deal (title, amount, stage, probability, close_date, contact, company, owner)
- Activity (type, subject, description, due_date, status, related_to, owner)
- Note (content, related_to, author, created_at)
- Pipeline (name, stages, deal_probability)
- Task (subject, due_date, status, priority, assigned_to, related_to)
- EmailTemplate (name, subject, body, variables)

## Common Workflows
1. Sales rep views pipeline → sees deals by stage → drags deal to next stage
2. Rep opens contact → views call history → logs new call activity
3. Rep creates deal → links to contact → sets amount → closes won
4. Manager views pipeline forecast → adjusts team targets
5. Automated email sequence → tracked opens/clicks → logged to contact
6. Report runs weekly → pipeline health → conversion rates → team ranking

## Common API Endpoints
| Method | Path | Action |
|--------|------|--------|
| GET | /api/contacts | List contacts with search, filter |
| GET | /api/contacts/:id | Contact detail with related data |
| POST | /api/contacts | Create contact |
| PUT | /api/contacts/:id | Update contact |
| GET | /api/deals | List deals (filter by stage, owner) |
| PUT | /api/deals/:id/stage | Update deal stage |
| GET | /api/pipeline | Pipeline with deals grouped by stage |
| POST | /api/activities | Log activity |
| GET | /api/activities/:contactId | Activity history for contact |
| GET | /api/reports/pipeline | Pipeline analytics |
| GET | /api/reports/forecast | Revenue forecast |

## Common UI Components
- **Kanban Board** — drag-and-drop deal cards by stage
- **Contact Table** — rows with name, company, email, phone, tags
- **Contact Detail Panel** — slide-out panel with tabs (info, activity, deals, notes)
- **Activity Timeline** — chronological feed of calls, emails, meetings, notes
- **Pipeline Summary Card** — stage name, deal count, total value
- **Deal Card** — title, amount, contact, probability, days open
- **Email Composer** — rich email editor with template picker
- **Smart Search** — unified search across contacts, deals, companies
- **Tag Manager** — color-coded tags with filtering

## Common Dashboards
- **Pipeline Dashboard**: total pipeline value (number card), deals by stage (bar), won/lost ratio (pie), conversion by stage (funnel)
- **Activity Dashboard**: calls made (bar), emails sent (line), meetings (number), activity by rep (table)
- **Team Dashboard**: each rep's pipeline value, deals closed, activities logged, conversion rate

## Common Reports
- Pipeline forecast (weighted by probability)
- Sales by rep (closed won amount, count, average deal size)
- Conversion rates (stage-to-stage)
- Aging deals (deals stalled in stage for X days)
- Activity metrics (calls/emails/meetings per rep per period)
- Lost deal analysis (reasons breakdown)
