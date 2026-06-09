# Dashboard — Product Pattern

## Common Pages
- **Main Dashboard** — aggregate KPIs, charts, recent activity
- **Analytics View** — detailed metrics with date range controls
- **Team Dashboard** — per-user/per-team metrics
- **Executive Summary** — high-level business health overview
- **Custom Dashboard** — user-configurable widget layout

## Common Entities
- Metric / KPI definition
- Dashboard layout / widget configuration
- User dashboard preference
- Data source / report definition

## Common Workflows
1. User lands on dashboard → sees key metrics for default time range
2. User adjusts date range → all charts update
3. User clicks a chart segment → drill-down to detail view
4. User adds/removes widgets → layout saves per user
5. Dashboard auto-refreshes on interval

## Common API Endpoints
| Method | Path | Action |
|--------|------|--------|
| GET | /api/dashboard/metrics | Aggregate KPI data |
| GET | /api/dashboard/charts/:type | Chart data (line, bar, pie) |
| GET | /api/dashboard/timeseries | Time-series data points |
| GET | /api/dashboard/recent-activity | Latest events |
| PUT | /api/dashboard/layout | Save user dashboard layout |

## Common UI Components
- **KPI Card** — icon, label, value, trend arrow, sparkline
- **Line/Area Chart** — time-series data with date range picker
- **Bar Chart** — categorical comparisons
- **Pie/Donut Chart** — distribution breakdowns
- **Metric Grid** — 2-4 column responsive grid of KPI cards
- **Date Range Picker** — preset ranges (7d, 30d, 90d, custom)
- **Activity Feed** — scrollable list of recent events
- **Widget Container** — draggable/resizable widget wrapper
- **Filter Bar** — global filters applied to all widgets

## Common Dashboards
- **Sales Dashboard**: revenue (line), top products (bar), conversion (funnel), recent orders (table)
- **Operations Dashboard**: uptime (gauge), error rate (sparkline), queue depth (bar), alerts (table)
- **User Dashboard**: active users (area), signups (bar), churn (line), cohorts (table)

## Common Reports
- Scheduled PDF/email of dashboard snapshot
- Export chart data as CSV
- Dashboard as presentation mode (full screen, no edit chrome)
