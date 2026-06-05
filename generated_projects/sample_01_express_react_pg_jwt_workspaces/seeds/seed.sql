INSERT INTO users (email, password_hash) VALUES
('admin@example.com', '$2a$10$8v8v8v8v8v8v8v8v8v8v8u8v8v8v8v8v8v8v8v8v8v8v8v8v8'),
('user@example.com', '$2a$10$9v9v9v9v9v9v9v9v9v9v9v9v9v9v9v9v9v9v9v9v9v9v9v9v9');

INSERT INTO workspaces (name, description, owner_id) VALUES
('Default Workspace', 'The default workspace for the admin user', 1),
('Personal Projects', 'Personal tasks and side projects', 2);

INSERT INTO projects (name, description, workspace_id) VALUES
('Website Redesign', 'Redesign the company website', 1),
('Mobile App', 'Build a mobile app for clients', 2);

INSERT INTO tasks (title, description, status, project_id, assigned_to) VALUES
('Design homepage', 'Create wireframes for the homepage', 'todo', 1, 1),
('Setup CI/CD', 'Configure GitHub Actions', 'in-progress', 1, 1),
('Prototype UI', 'Build interactive prototype', 'todo', 2, 2);