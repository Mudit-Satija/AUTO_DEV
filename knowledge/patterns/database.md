# Database Schema and Seeding Best Practices

Ensure database migrations and seed scripts adhere strictly to the following standards:

## SQL (PostgreSQL/MySQL/SQLite)
- Always use `CREATE TABLE IF NOT EXISTS` for all tables.
- Define a primary key (e.g., `id SERIAL PRIMARY KEY` or `id VARCHAR(36) PRIMARY KEY`) for every table.
- Enforce relational integrity using explicit `FOREIGN KEY` constraints.
- Structure SQL schemas in migration files (e.g., `migrations/001_initial.sql`).
- Structure developer mock data in seed files (e.g., `seeds/seed.sql`) using `INSERT INTO ...` statements.

## MongoDB (NoSQL)
- Always clear existing documents in collections before inserting new seeds (`deleteMany({})`).
- Write seed files (`seeds/seed.js` or `seeds/seed.py`) to connect to the database, seed all entities, and close connection cleanly.
- Ensure collections map exactly to the entities listed in the SRS.
