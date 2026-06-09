# Bulletproof React — Architecture Knowledge

## Folder Structure Conventions
```
src/
├── app/              # application layer: routes, App.tsx, provider.tsx, router.tsx
├── assets/           # static files (images, fonts)
├── components/       # shared components across entire app
├── config/           # global config, env vars
├── features/         # feature-based modules (core organizing principle)
├── hooks/            # shared hooks
├── lib/              # preconfigured libraries (api client, etc.)
├── stores/           # global state stores
├── testing/          # test utilities and mocks
├── types/            # shared TypeScript types
└── utils/            # shared utility functions
```

## Feature Module Structure
```
src/features/awesome-feature/
├── api/        # API request declarations + hooks
├── assets/     # feature-specific static files
├── components/ # feature-specific components
├── hooks/      # feature-specific hooks
├── stores/     # feature-specific state stores
├── types/      # feature-specific types
└── utils/      # feature-specific utils
```

## Project Organization
- Feature-based modular architecture — features are independent
- Cross-feature imports forbidden via ESLint (`import/no-restricted-paths`)
- Enforces unidirectional code flow: shared → features → app
- Barrel files discouraged (hurts Vite tree-shaking)
- Each feature owns its API, components, hooks, types, and utils

## API Organization
- Single pre-configured API client instance (axios/fetch)
- API request declarations colocated per feature in `features/<name>/api/`
- Each declaration has: types + validation schemas, a fetcher function, and a hook
- Hooks built on react-query/SWR
- Typed responses inferred throughout the app

## Service Layer Patterns
- Business logic lives inside feature modules
- Data fetching abstracted into hooks wrapping react-query (queries & mutations)
- No traditional "service layer" — logic split between hooks and API declarations

## State Management Patterns
1. **Component state** — `useState`/`useReducer` (local only)
2. **Application state** — context+hooks, Redux Toolkit, zustand, jotai (modals, notifications, theme)
3. **Server cache state** — react-query, SWR, Apollo, RTK
4. **Form state** — React Hook Form / Formik with zod/yup validation
5. **URL state** — react-router params/query strings
- Minimize global state; keep state close to where it's used

## Routing Conventions
- Routes defined in `src/app/routes/` using react-router-dom
- Layout routes wrap child routes
- Each feature typically gets a route segment
- URL parameters for dynamic data
- Nested routing patterns with `<Outlet />`

## Validation Patterns
- Client-side form validation using zod or yup integrated with React Hook Form
- API response validation via TypeScript types

## Error Handling Patterns
- API errors: interceptor catches all HTTP errors, shows notification toasts, handles 401
- In-app errors: React Error Boundaries at multiple granular levels
- Production error tracking: Sentry with source maps

## Scalability Principles
- Feature isolation prevents spaghetti
- Unidirectional data flow ensures predictability
- Colocation reduces cognitive load
- Forbidding cross-feature imports enforces modularity
- Choosing right state category prevents over-engineering
- Single API client centralizes configuration
