# Node.js Best Practices — Architecture Knowledge

## Folder Structure Conventions
```
my-system/
├── apps/ (components)     # business modules
│   ├── orders/
│   ├── users/
│   └── payments/
└── libraries/             # generic cross-component utilities
    ├── logger/
    │   ├── package.json
    │   └── src/index.js
    └── authenticator/
```

## Component 3-Tier Layering
```
component-a/
├── entry-points/    # api (controllers), message-queue (consumers)
├── domain/          # DTOs, services, business logic
└── data-access/     # DB calls without ORM
```

## Project Organization
- Structure by business components (bounded contexts), not by technical roles
- Each component has its own API, logic, and logical database
- Common utilities wrapped as independent packages with own `package.json`
- Supports monorepo or multi-repo

## API Organization
- Separate web layer from domain layer
- Controllers belong in `entry-points/api/`
- Never pass request/response objects into domain logic
- Document API errors using OpenAPI or GraphQL
- Use consistent route naming

## Service Layer Patterns
- Domain folder in each component contains features, flows, DTOs, services, business logic
- Services are plain JavaScript/TypeScript objects with no HTTP/DB coupling
- Cross-component communication through well-defined interfaces, not direct internal imports

## State Management Patterns (Backend)
- Strive to be stateless — store session data in external stores (Redis, DB)
- Use environment-aware hierarchical config
- Config read from both file and env vars

## Routing Conventions
- Nest.js recommended for large-scale OOP apps
- Fastify recommended for microservices/components approach
- Express for simpler needs
- Koa as alternative

## Validation Patterns
- Fail fast — validate arguments using dedicated libraries (ajv, zod, typebox)
- Validate incoming JSON schemas
- Validate config at startup
- Use strong input validation to prevent injection attacks

## Error Handling Patterns
- Use async-await with try-catch
- Extend built-in Error with custom properties (name/code, isCatastrophic)
- Distinguish operational (handle gracefully) vs programmer errors (crash & restart)
- Centralized error handler — one object all entry-points call
- Document API errors
- Exit gracefully on unknown errors
- Use mature logger (Pino/Winston)
- Test error flows
- Catch unhandled promise rejections
- Always `return await`
- Subscribe to 'error' event on emitters/streams

## Scalability Principles
- Component-based architecture enables teams to own autonomous modules
- 3-tier layering enforces separation of concerns
- Wrapping utilities as packages creates clear public interfaces
- Config is hierarchical, typed, validated
- Focus on API tests first (most coverage for effort)
- Keep app stateless for horizontal scaling
