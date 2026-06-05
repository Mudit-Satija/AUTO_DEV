INSERT INTO users (username, email, hashed_password) VALUES
('admin', 'admin@example.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW'),
('user1', 'user1@example.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW'),
('user2', 'user2@example.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW');

INSERT INTO tokens (user_id, token, expires_at) VALUES
(1, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjEsImV4cCI6MTc5ODc2NTYwMH0.4qJq8jJZv8u8v8v8v8v8v8v8v8v8v8v8v8v8v8v8v8', '2025-12-31 23:59:59+00'),
(2, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjIsImV4cCI6MTc5ODc2NTYwMH0.4qJq8jJZv8u8v8v8v8v8v8v8v8v8v8v8v8v8v8', '2025-12-31 23:59:59+00'),
(3, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjMsImV4cCI6MTc5ODc2NTYwMH0.4qJq8jJZv8u8v8v8v8v8v8v8v8v8v8v8v8v8v8', '2025-12-31 23:59:59+00');