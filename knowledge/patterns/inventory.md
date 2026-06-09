# Inventory — Product Pattern

## Common Pages
- **Inventory List** — table of all items with stock levels, filters
- **Item Detail** — single item view with history
- **Stock In** — form to add stock (purchase order, manual add)
- **Stock Out** — form to deduct stock (sale, write-off, transfer)
- **Inventory Adjustments** — correction log with reason
- **Low Stock Alerts** — items below threshold
- **Transfer** — move stock between locations/warehouses
- **Bulk Import** — upload CSV/XLSX to update inventory

## Common Entities
- SKU (unique product code)
- Product name, description, category
- Quantity on hand, reserved, available
- Reorder point / min-max levels
- Location / warehouse / bin
- Supplier, cost price, selling price
- Batch/lot number, expiry date
- Unit of measure (each, kg, box)

## Common Workflows
1. Stock arrives → record purchase order → quantity increases
2. Stock sold → quantity decreases (reserved before confirmed)
3. Stock below threshold → alert triggers → reorder initiated
4. Physical count → adjust quantities → audit log updated
5. Transfer between warehouses → source decrements, destination increments

## Common API Endpoints
| Method | Path | Action |
|--------|------|--------|
| GET | /api/inventory | List inventory with stock levels |
| GET | /api/inventory/:id | Item detail |
| POST | /api/inventory/stock-in | Add stock |
| POST | /api/inventory/stock-out | Remove stock |
| POST | /api/inventory/adjust | Adjust quantity with reason |
| GET | /api/inventory/alerts | Low stock alerts |
| POST | /api/inventory/transfer | Transfer between locations |
| GET | /api/inventory/history/:id | Movement history for item |
| POST | /api/inventory/bulk-import | Bulk upload |

## Common UI Components
- **Data Table** — sortable, filterable inventory list with color-coded stock levels
- **Stock Status Badge** — in-stock (green), low (yellow), out (red)
- **Quantity Adjuster** — +/- buttons or numeric input
- **Location Picker** — warehouse/bin selector (tree or dropdown)
- **Movement Timeline** — chronological view of stock changes
- **Alert Card** — low-stock items listed with reorder button
- **Bulk Import Modal** — file upload with preview and validation errors

## Common Dashboards
- Stock value by category (pie chart)
- Movement velocity (top movers in/out)
- Low stock count (number card)
- Inventory turnover rate (line chart)
- Stock accuracy vs physical count (gauge)

## Common Reports
- Stock valuation report
- Low stock / out of stock report
- Inventory movement summary (daily/weekly/monthly)
- Physical count sheet (export for offline counting)
- Reorder suggestions
