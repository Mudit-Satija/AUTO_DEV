INSERT INTO users (username, email, hashed_password, oauth_provider, oauth_id) VALUES
('john_doe', 'john.doe@example.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'google', '1234567890'),
('jane_smith', 'jane.smith@example.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'github', '0987654321'),
('admin_user', 'admin@example.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', NULL, NULL);

INSERT INTO tokens (user_id, access_token, refresh_token, expires_at) VALUES
(1, 'access_token_123', 'refresh_token_123', '2025-12-31 23:59:59+00'),
(2, 'access_token_456', 'refresh_token_456', '2025-12-31 23:59:59+00'),
(3, 'admin_access_token', 'admin_refresh_token', '2025-12-31 23:59:59+00');