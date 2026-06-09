# Magic UI — Design Knowledge

## Design Philosophy
- "UI Library for Design Engineers" — landing-page focused
- "Good design contributes significant value to software. It establishes trust."
- Copy-paste model (inspired by shadcn/ui)
- Primarily for landing pages, marketing sites, and user-facing materials
- Heavily animated, visually impressive components

## Layout Patterns
- Bento grids as primary layout pattern (`<BentoGrid />`)
- No traditional dashboard layouts
- Full-page templates: landing pages, SaaS, startup, portfolio
- Hero sections as centerpiece layouts

## Dashboard Patterns
- None — not designed for dashboards
- No charts, KPIs, or data visualization components

## Table Patterns
- None — no table components at all

## Form Patterns
- Minimal — only `<SignupForm />` in some templates
- Not a form-focused library

## Navigation Patterns
- `<Dock />` — macOS-style floating dock
- `<FloatingNavbar />`
- TabNavigation-like patterns in templates
- No sidebar component

## Responsiveness
- Tailwind responsive by default
- Components designed for modern landing pages — mobile-friendly
- Device mock components: Safari, iPhone, Android browser frames

## Accessibility
- No explicit accessibility documentation
- Radix UI not used as base
- Focus on visual effects over a11y
- Community components vary in quality

## Components to Prefer
- `<Marquee />` — infinite scrolling logos/text
- `<BentoGrid />` — featured grid layouts
- `<AnimatedBeam />`, `<BorderBeam />`, `<ShineBorder />` — decorative effects
- `<Globe />` — 3D globe visualization
- `<TextAnimate />`, `<TypingAnimation />`, `<NumberTicker />` — text animations
- `<RainbowButton />`, `<ShimmerButton />` — visually rich buttons
- `<AnimatedList />`, `<AvatarCircles />`, `<OrbitingCircles />`
- Background patterns: `<RetroGrid />`, `<DotPattern />`, `<GridPattern />`, `<Ripple />`

## Components to Avoid
- No form components (use shadcn/ui)
- No data tables
- No charts/dashboard components
- No sidebar/navigation menus for apps
- Animation-heavy components may impact performance if overused
- Many effects are Pro/paid
