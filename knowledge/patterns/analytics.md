# Analytics — Product Pattern

## Common Pages
- **Overview Dashboard** — top-level metrics with time comparison
- **User Analytics** — acquisition, retention, engagement, cohorts
- **Revenue Analytics** — MRR, ARR, churn, LTV, funnel conversion
- **Performance Analytics** — response times, error rates, uptime
- **Custom Reports** — query builder with save/share
- **Data Explorer** — raw data view with filters, aggregation, export

## Common Entities
- Event / action (user signed up, order placed)
- User session with duration and page views
- Conversion funnel step
- Cohort definition and membership
- Report definition (filters, metrics, dimensions)
- Dashboard widget configuration

## Common Workflows
1. User selects metric group and date range
2. System returns aggregate data with period-over-period comparison
3. User applies filters (by segment, geography, source)
4. User saves view as report or adds to dashboard
5. Report is exported or shared via link
6. Scheduled report is emailed on interval

## Common API Endpoints
| Method | Path | Action |
|--------|------|--------|
| GET | /api/analytics/query | Run aggregate query |
| GET | /api/analytics/timeseries | Time-series data points |
| GET | /api/analytics/funnel | Conversion funnel steps |
| GET | /api/analytics/cohorts | Cohort analysis |
| GET | /api/analytics/retention | Retention curve data |
| POST | /api/analytics/reports | Save custom report |
| GET | /api/analytics/reports/:id | Load saved report |
| POST | /api/analytics/export | Export data (CSV/PDF) |

## Common UI Components
- **Metric Card** — value, % change, sparkline, comparison label
- **Time Series Chart** — line/area chart with date range selector
- **Funnel Chart** — step-by-step conversion visualization
- **Cohort Table** — grid of cohort retention percentages
- **Pivot Table** — drag-and-drop dimension/metric builder
- **Filter Bar** — multi-select filters for segment, source, date
- **Date Range Picker** — presets + custom range, compare mode
- **Chart Builder** — pick chart type, metrics, dimensions, sort
- **Export Button** — CSV, PDF, PNG, scheduled email

## Common Dashboards
- **Marketing Dashboard**: traffic (area), conversion (funnel), CPA (bar), ROAS (number card)
- **Product Dashboard**: DAU/MAU (line), retention (cohort), feature adoption (bar), funnel (conversion)
- **Business Dashboard**: revenue (line), expenses (bar), profit (number), burn rate (sparkline)

## Common Reports
- Weekly/Monthly performance report (PDF)
- Automated anomaly detection alert
- Trend analysis with forecast
- Segment comparison report
- Raw data export with applied filters
