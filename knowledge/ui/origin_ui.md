# Origin UI — Design Knowledge

## Design Philosophy
- Originally Radix-based shadcn-style components, acquired by Cal.com
- Active development on "Particles" built on Base UI + Tailwind CSS
- Legacy Origin UI components available but limited support
- Copy-paste distribution model like shadcn/ui
- "Build beautiful, reliable user interfaces."

## Layout Patterns
- Standard Tailwind-based layouts
- No unique layout system — follows shadcn conventions
- Particles (new) and Origin (legacy) components can be mixed

## Dashboard Patterns
- Minimal documentation — no standout dashboard patterns yet
- Being progressively adopted for cal.com (scheduling app)
- Dashboard support is evolving

## Table Patterns
- Basic table component (inherits from shadcn-style)
- No advanced data table pattern documented yet

## Form Patterns
- Standard form components: Input, Select, Textarea, Checkbox, Radio, Switch
- Follows Radix UI primitives

## Navigation Patterns
- Standard: Tabs, DropdownMenu, NavigationMenu
- No unique sidebar component documented

## Responsiveness
- Tailwind responsive — standard shadcn patterns
- Documentation built with Fumadocs

## Accessibility
- Base UI primitives provide WAI-ARIA compliance
- Radix-based legacy Origin components also accessible

## Components to Prefer (Particles — new)
- Any new "Particles" components built on Base UI
- Components being adopted for cal.com (likely form-heavy)
- The new primitives over legacy Origin ones

## Components to Avoid
- Legacy Origin UI components (limited support/maintenance)
- No advanced dashboard/table patterns yet
- Library is in transition — check docs for stability
- Less mature than shadcn/ui or Tremor
