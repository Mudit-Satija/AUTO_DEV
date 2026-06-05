INSERT INTO roles (name) VALUES ('admin'), ('editor'), ('viewer');

INSERT INTO permissions (name) VALUES ('create_user'), ('read_user'), ('update_user'), ('delete_user'), ('create_role'), ('read_role'), ('update_role'), ('delete_role'), ('create_permission'), ('read_permission'), ('update_permission'), ('delete_permission');

INSERT INTO role_permissions (role_id, permission_id) VALUES
(1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7), (1, 8), (1, 9), (1, 10), (1, 11), (1, 12),
(2, 2), (2, 3), (2, 6), (2, 7), (2, 10), (2, 11),
(3, 2), (3, 6), (3, 10);

INSERT INTO users (username, email, password_hash) VALUES
('admin', 'admin@example.com', '$2a$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi'),
('editor', 'editor@example.com', '$2a$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi'),
('viewer', 'viewer@example.com', '$2a$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi');

INSERT INTO user_roles (user_id, role_id) VALUES
(1, 1),
(2, 2),
(3, 3);