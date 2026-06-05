INSERT INTO users (username, email, hashed_password) VALUES
('admin', 'admin@example.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW'),
('user1', 'user1@example.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW');

INSERT INTO oauth_clients (client_id, client_secret, redirect_uri) VALUES
('client1', 'secret1', 'http://localhost:3000/auth/callback'),
('client2', 'secret2', 'http://localhost:3000/auth/callback');

INSERT INTO oauth_tokens (user_id, client_id, access_token, refresh_token, expires_at, scope) VALUES
(1, 'client1', 'access_token_123', 'refresh_token_123', '2025-12-31 23:59:59+00', 'read write'),
(2, 'client1', 'access_token_456', 'refresh_token_456', '2025-12-31 23:59:59+00', 'read');