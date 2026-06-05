INSERT INTO customers (name, email, phone) VALUES
('John Doe', 'john.doe@example.com', '555-1234'),
('Jane Smith', 'jane.smith@example.com', '555-5678'),
('Bob Johnson', 'bob.johnson@example.com', '555-9012');

INSERT INTO inventory (item_name, description, quantity, unit_price) VALUES
('Laptop', 'High-performance laptop', 10, 999.99),
('Mouse', 'Wireless mouse', 50, 29.99),
('Keyboard', 'Mechanical keyboard', 30, 149.99);

INSERT INTO orders (customer_id, total_amount, status) VALUES
(1, 1029.98, 'completed'),
(2, 29.99, 'pending'),
(3, 149.99, 'shipped');

INSERT INTO order_items (order_id, inventory_id, quantity, price_at_time) VALUES
(1, 1, 1, 999.99),
(1, 2, 1, 29.99),
(2, 2, 1, 29.99),
(3, 3, 1, 149.99);