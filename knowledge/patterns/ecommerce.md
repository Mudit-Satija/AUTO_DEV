# E-Commerce — Product Pattern

## Common Pages
- **Product Catalog** — grid/list view with filtering and search
- **Product Detail** — images, specs, price, add-to-cart
- **Cart** — line items, quantity adjust, coupon, checkout button
- **Checkout** — shipping info, payment, order review
- **Order Confirmation** — success page with order summary
- **Order History** — list of past orders with status
- **Order Detail** — single order with line items, tracking
- **Admin Products** — CRUD for product management
- **Admin Orders** — order management, fulfillment, refund
- **Admin Categories** — category tree management

## Common Entities
- Product (SKU, name, description, price, images, category, variants)
- Category (name, slug, parent, description)
- Cart / CartItem
- Order (number, status, total, shipping, payment info)
- OrderItem (product, quantity, unit price)
- Customer (name, email, addresses, order history)
- Payment (method, transaction ID, status)
- Shipment (carrier, tracking number, status)
- Review (rating, text, product, customer)

## Common Workflows
1. Browse catalog → filter by category/price/search
2. View product detail → select variant → add to cart
3. View cart → adjust quantities → apply coupon → proceed to checkout
4. Enter shipping info → select payment method → place order
5. Receive confirmation email → order fulfilled → tracking number sent
6. Leave review after delivery

## Common API Endpoints
| Method | Path | Action |
|--------|------|--------|
| GET | /api/products | List with filtering, sorting, pagination |
| GET | /api/products/:id | Product detail with variants |
| GET | /api/categories | Category tree |
| GET/POST | /api/cart | Get or update cart |
| POST | /api/checkout | Place order |
| GET | /api/orders | Customer order history |
| GET | /api/orders/:id | Order detail with tracking |
| POST | /api/payments | Process payment |
| POST | /api/reviews | Submit product review |

## Common UI Components
- **Product Card** — image, name, price, rating, add-to-cart button
- **Product Grid** — responsive grid (2-4 columns) of product cards
- **Filter Sidebar** — category tree, price range, rating, brand checkboxes
- **Search Bar** — autocomplete with product suggestions
- **Cart Drawer** — slide-out panel with cart summary
- **Checkout Stepper** — multi-step progress (info → shipping → payment → confirm)
- **Order Status Timeline** — ordered → confirmed → shipped → delivered
- **Review Stars** — clickable star rating with text input

## Common Dashboards
- **Sales Dashboard**: revenue (line), orders (bar), AOV (number), top products (table)
- **Inventory Dashboard**: stock alerts, low stock items, category breakdown (pie)
- **Customer Dashboard**: new vs returning, LTV, order frequency

## Common Reports
- Daily/weekly/monthly sales report
- Top-selling products
- Inventory valuation
- Customer acquisition and retention
- Abandoned cart analysis
