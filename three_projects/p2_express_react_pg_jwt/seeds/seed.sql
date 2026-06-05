INSERT INTO users (username, email, password_hash) VALUES
('admin', 'admin@example.com', '$2a$10$examplehash1234567890123456789012345678901234567890123456789'),
('user1', 'user1@example.com', '$2a$10$examplehash0987654321098765432109876543210987654321098765432');

INSERT INTO products (name, description, price, stock_quantity) VALUES
('Laptop', 'High-performance laptop for professionals', 999.99, 10),
('Mouse', 'Wireless ergonomic mouse', 29.99, 50),
('Keyboard', 'Mechanical gaming keyboard', 129.99, 25);

INSERT INTO orders (user_id, total_amount, status) VALUES
(1, 1029.98, 'completed'),
(2, 29.99, 'pending');

INSERT INTO order_items (order_id, product_id, quantity, price_at_time) VALUES
(1, 1, 1, 999.99),
(1, 2, 1, 29.99),
(2, 2, 1, 29.99);