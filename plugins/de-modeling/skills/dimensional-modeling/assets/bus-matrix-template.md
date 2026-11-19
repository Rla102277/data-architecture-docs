# Bus matrix

Rows are business processes (one fact table each). Columns are conformed
dimensions. An X means the fact carries that dimension.

| Business process (fact) | Grain | Date | Customer | Product | Location | Employee | Channel | Owner |
|---|---|---|---|---|---|---|---|---|
| Orders (fct_order_lines) | one row per order line | X | X | X | X | X | X | |
| Shipments (fct_shipments) | one row per shipment line | X | X | X | X | | | |
| Inventory (fct_inventory_daily) | one row per product per location per day | X | | X | X | | | |

Dimension owners:

| Dimension | Business key | SCD policy | Owner |
|---|---|---|---|
| dim_customer | customer_id | Type 2 on segment and territory, Type 1 otherwise | |
| dim_product | product_id | Type 2 on category | |
| dim_date | date | static | |
