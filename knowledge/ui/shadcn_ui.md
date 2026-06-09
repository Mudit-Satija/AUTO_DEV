# shadcn/ui — Design Knowledge

## Design Philosophy
- NOT a component library — "how you build your component library"
- Copy-paste distribution: you own the full source, no npm dependency
- Composition over configuration: predictable composable APIs
- AI-Ready: open code makes it easy for LLMs to read, understand, generate
- Beautiful defaults, fully customizable via CSS variables
- Built on Radix UI primitives (WAI-ARIA compliant)

## Layout Patterns
- No built-in grid system — use Tailwind grid/flex
- Blocks library provides full page examples (sidebar + main)
- Resizable panels via `<Resizable />`
- Card grouping: `CardHeader`, `CardContent`, `CardFooter`
- Container pattern: `mx-auto py-10`

## Dashboard Patterns
- Charts via `<Chart />` wrapping Recharts v3 (area, bar, line, pie, radial)
- Chart config object: labels, icons, theme colors (`chart-1` to `chart-5` CSS vars)
- Composables: `ChartTooltip`, `ChartLegend`, `ChartContainer`
- Cards for KPI display, customizable radius scale

## Table Patterns
- No single `<DataTable />` — guide using TanStack Table + `<Table />` primitive
- Column definitions: sorting, filtering, visibility toggle, row selection, pagination
- Reusable: `DataTableColumnHeader`, `DataTablePagination`, `DataTableViewOptions`
- Primitives: `Table`, `TableHeader`, `TableBody`, `TableRow`, `TableCell`, `TableHead`

## Form Patterns
- Three framework options: React Hook Form, TanStack Form, Formisch
- Composables: `Field`, `FieldLabel`, `FieldDescription`, `FieldError`, `FieldGroup`
- Uses `Controller` from RHF for controlled inputs
- Zod schema validation with `zodResolver`
- All input types: input, textarea, select, checkbox, radio group, switch, array fields
- Orientation prop on Field (vertical/horizontal/responsive)
- `aria-invalid` + `data-invalid` for error states

## Navigation Patterns
- `<Sidebar />` ecosystem: SidebarProvider, Sidebar, SidebarHeader, SidebarContent, SidebarFooter, SidebarGroup, SidebarMenu, SidebarMenuItem, SidebarMenuButton, SidebarMenuSub, SidebarRail, SidebarTrigger
- Three variants: sidebar (default), floating, inset
- Three collapsible modes: offcanvas, icon, none
- Keyboard shortcut: cmd+b / ctrl+b
- Also: NavigationMenu, Tabs, Breadcrumb, Menubar, DropdownMenu

## Responsiveness
- Tailwind-responsive by default, mobile-first
- Sidebar collapses to bottom sheet on mobile (uses Sheet)
- Sidebar widths: `SIDEBAR_WIDTH` (desktop), `SIDEBAR_WIDTH_MOBILE`
- Responsive prop on Field (`orientation="responsive"`)
- Cards use `@container` queries

## Accessibility
- Radix UI primitives — WAI-ARIA compliant
- `aria-invalid` on form controls, `sr-only` for screen reader text
- `accessibilityLayer` prop on charts for keyboard nav + screen reader
- Focus rings via `--ring` CSS variable
- RTL support throughout via `dir` prop

## Components to Prefer
- `<Sidebar />` — best-in-class sidebar experience
- `<Table />` with TanStack Table guide — most flexible table system
- `<Chart />` with Recharts v3 — beautiful default styling
- `<Card />` with `size` prop and `--card-spacing` variable
- `<Field />` form system — highly composable
- `<Dialog />`, `<Sheet />`, `<Drawer />` — modal/overlay trifecta
- `<Button />` variants, `<Badge />`, `<Command />` (cmdk)

## Components to Avoid
- No built-in DataTable component (use TanStack Table guide)
- No built-in dashboard layout (compose from Sidebar + Cards)
- No auth flows
- No complex animation system (use Framer Motion separately)
- No advanced form builders beyond Field primitives
