# Tremor — Design Knowledge

## Design Philosophy
- "Copy & paste React components to build charts and dashboards."
- Designed specifically for dashboards, data visualization, and admin panels
- Built on Tailwind CSS v4 + Radix UI
- Apache 2.0 licensed
- Acquired by Vercel
- Blocks & Templates at blocks.tremor.so
- Copy-paste model, not npm package

## Layout Patterns
- Dashboard-first: cards (KPI cards), grid layouts for chart arrangement
- `<Card />` as fundamental building block for KPI/metric cards
- `<Divider />` for section separation
- `<TabNavigation />` for top-level navigation between dashboard views
- Combobox, layout templates (free Next.js dashboard template)
- Responsive grid layouts via Tailwind

## Dashboard Patterns
- Charts: Area, Bar, Combo, Donut, Line — all using Recharts
- Progress: `<ProgressBar />`, `<ProgressCircle />` for KPI progress
- `<SparkChart />`: inline sparkline charts for compact metrics
- `<BarList />`: horizontal bar lists for ranking/breakdown data
- `<CategoryBar />`: segmented progress/category display
- `<Tracker />`: timeline/activity tracker visualization
- Card-based KPIs: typical pattern is `<Card>` containing chart or stat
- All charts support: `onValueChange` click events, custom tooltips, legends, axis labels
- `chartUtils.ts` utility for consistent chart colors and helpers
- `valueFormatter` pattern for number/currency formatting

## Table Patterns
- `<Table />`, `<TableBody>`, `<TableHead>`, `<TableHeaderCell>`, `<TableRow>`, `<TableCell>`, `<TableFoot>`, `<TableCaption>`
- Styled for dashboards — clean, minimal, dark mode support
- `<TableRoot>` wrapper for scrollable overflow on mobile
- Manual data mapping (no TanStack Table out of box)
- Badges inside tables for status indicators

## Form Patterns
- Input: `<Input />`, `<Textarea />`, `<Select />`, `<SelectNative />`
- Selection: `<Checkbox />`, `<RadioGroup />`, `<RadioCardGroup />`, `<Switch />`, `<Toggle />`
- Date: `<Calendar />`, `<DatePicker />`, `<DateRangePicker />`
- `<DropdownMenu />` for action menus
- `<Slider />` for range inputs
- `<Label />` for form labels
- Focus/hover utilities: `focusInput`, `hasErrorInput`, `focusRing`
- Themed input styling with `--input` CSS variable

## Navigation Patterns
- `<TabNavigation />` — dashboard tab navigation (top-level)
- `<Tabs />` — tab switching within pages
- `<Accordion />` for collapsible sections
- `<DropdownMenu />` for dropdowns
- No sidebar component (use shadcn sidebar with Tremor)

## Responsiveness
- Tailwind responsive utilities
- Tables scrollable on mobile via `overflow-auto whitespace-nowrap`
- Dashboard template responsive by default
- `TableRoot` component provides horizontal scroll
- Charts use `ResponsiveContainer` from Recharts

## Accessibility
- Built on Radix UI — WAI-ARIA compliant overlays and inputs
- `tremor-id="tremor-raw"` on components for scoping
- Charts support keyboard navigation and `onValueChange` for interactivity
- Focus ring utilities provided
- Screen reader support in tooltips and legends
- Dark mode CSS variables throughout

## Components to Prefer
- All chart types (Area, Bar, Line, Donut, Combo) — best-in-class for dashboards
- `<SparkChart />` — compact inline metrics
- `<BarList />` — ranking/top-N lists
- `<CategoryBar />` — progress categories
- `<Tracker />` — timeline activity
- `<Card />` — KPI card container
- `<ProgressCircle />`, `<ProgressBar />`
- `<Badge />` — status indicators in tables
- `<DateRangePicker />` — date range filtering
- `<TabNavigation />` — dashboard navigation
- `<Table />` with Badges — data display

## Components to Avoid
- No sidebar component (use shadcn)
- No complex form system (use shadcn Field + RHF)
- Table is basic HTML — no sorting/filtering built in (use TanStack Table separately)
- No authentication/login components
- No animated/landing page components (use Magic UI or Aceternity)
- No command palette (use shadcn Command)
- Charts require Recharts v3 dependency
