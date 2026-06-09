# Aceternity UI — Design Knowledge

## Design Philosophy
- "Ship landing pages at lightning speed."
- 200+ production-ready components, blocks, and templates
- Copy-paste model compatible with shadcn/ui
- Heavy Framer Motion animations — visual wow factor
- Freemium: free components + paid "All-Access Pass"
- Built by Manu Arora — community-driven

## Layout Patterns
- Bento grids, hero sections, feature grids, pricing tables
- Layout grid with Framer Motion layout animations
- No traditional app dashboard layout
- Template-based: SaaS, portfolio, marketing, agency

## Dashboard Patterns
- None — no charts, KPIs, or data dashboards
- Some stats sections for displaying numbers

## Table Patterns
- None — no data tables

## Form Patterns
- Signup form component (wrapper around shadcn inputs + Framer Motion)
- `<PlaceholdersAndVanishInput />` — animated input with placeholder cycling
- `<FileUpload />` — drag-and-drop
- `<GooeyInput />` — expanding search input
- Not a form library — minimal coverage

## Navigation Patterns
- `<FloatingNavbar />` — hides on scroll down, reveals on scroll up
- `<NavbarMenu />` — animated mega menu
- `<Sidebar />` — expandable sidebar (similar to shadcn)
- `<FloatingDock />` — macOS-style dock
- `<Notch />` — pinned floating notch
- `<Tabs />` — animated tab switching
- `<ResizableNavbar />` — width changes on scroll

## Responsiveness
- Fully responsive across all device sizes
- Mobile hamburger menus in templates
- Tailwind CSS responsive utilities

## Accessibility
- Not explicitly documented
- Framer Motion animations may interfere with prefers-reduced-motion
- Focus more on visual impact than accessibility guarantees
- shadcn-compatible components inherit Radix a11y

## Components to Prefer (Premium/Paid)
- Hero sections (21+ blocks), Bento Grids, Backgrounds
- 3D Globe, 3D Card Effect, 3D Pin
- Sparkles, Spotlight, Tracing Beam, Lamp Effect
- Animated Tooltip, Animated Modal
- Floating Dock, Sidebar
- Macbook Scroll, Parallax Scroll, Container Scroll Animation
- Card Hover Effect, Evervault Card, Wobble Card
- Text effects: Typewriter, Text Generate, Flip Words

## Components to Avoid
- No charts, tables, or data components
- Form support is minimal (only signup/file upload)
- Animations can be heavy — use sparingly
- Pro features are paid ($169)
- Not suitable for data-heavy dashboards or admin panels
- Accessibility not a priority
