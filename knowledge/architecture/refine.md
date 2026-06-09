# Refine — Architecture Knowledge

## Folder Structure Conventions
- Monorepo with `packages/` directory containing modular packages
- Each package independently versioned and published
- Core package (`@refinedev/core`) is the meta-framework
- UI packages: antd, mui, mantine, chakra
- Router packages: react-router, nextjs, remix
- Data provider packages: simple-rest, graphql, supabase, strapi, hasura, airtable

## Project Organization
- Headless React meta-framework for CRUD-heavy enterprise apps
- Decouples business logic from UI and routing via provider pattern
- Resources defined declaratively and mapped to routes
- Supports any UI framework (Ant Design, MUI, Mantine, Chakra UI)
- Supports any platform (Next.js, Remix, React Native, Electron)

## API Organization
- Provider-based: `dataProvider` abstracts data fetching
- Resources map entities to CRUD operations
- Auto-generates list/create/edit/show pages
- Supports SSR with Next.js/Remix
- 15+ backend connectors available

## Service Layer Patterns
- Business logic lives inside hooks (`useMany`, `useCreate`, `useUpdate`, `useDelete`)
- Hooks built on React Query
- Hooks interact with `dataProvider` and handle caching, loading, optimistic updates
- Customization via `resources` config and provider overrides

## State Management Patterns
- React Query (TanStack Query) as primary server state manager
- Hooks auto-manage loading, error, success states
- Client state via React context or any solution (Redux, Zustand, etc.)
- Built-in state for auth, routing, i18n via providers

## Routing Conventions
- `routerProvider` abstraction supports react-router, Next.js, Remix
- Resources auto-generate routes for list/create/edit/show
- Nested routes via `Outlet`
- URL parameters for resource IDs

## Validation Patterns
- Integrates with form libraries (Ant Design Form, MUI, React Hook Form)
- Validation depends on UI framework chosen

## Error Handling Patterns
- Error states returned from all hooks
- `useMutation`-based hooks provide `onError` callbacks
- Notification system for error/success feedback integrated with UI frameworks

## Scalability Principles
- Provider pattern makes backends/routers/UI swappable without code changes
- Headless architecture decouples UI from logic
- Hooks auto-manage CRUD boilerplate
- Monorepo organization enables modular feature adoption
- Resources abstraction standardizes data operations across the entire app
- Built for data-intensive admin panels
