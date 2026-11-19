# Layouts

## Medallion style

```
models/
+-- staging/                 # bronze/silver boundary: one model per source table, rename, cast, dedupe
|   +-- erp/
|   |   +-- _erp__sources.yml
|   |   +-- _erp__models.yml
|   |   +-- stg_erp__orders.sql
|   |   `-- stg_erp__order_lines.sql
|   `-- crm/
+-- intermediate/            # silver: joins and business logic, not exposed to BI
|   `-- sales/
|       `-- int_order_lines__enriched.sql
`-- marts/                   # gold: facts and dimensions consumers use
    +-- finance/
    |   +-- _finance__models.yml
    |   `-- fct_revenue.sql
    `-- core/
        +-- dim_customer.sql
        `-- dim_date.sql
```

## Data Vault plus marts

```
models/
+-- staging/                 # hashed, typed staging per source (AutomateDV / datavault4dbt stage macros)
+-- raw_vault/
|   +-- hubs/                # hub_customer.sql
|   +-- links/               # link_customer_order.sql
|   `-- satellites/          # sat_customer_erp_details.sql
+-- business_vault/          # PIT, bridge, computed satellites
`-- marts/                   # Kimball stars built from the vault
```

## dbt_project.yml defaults

```yaml
models:
  my_project:
    +persist_docs: {relation: true, columns: true}
    staging:
      +materialized: view
      +schema: staging
    intermediate:
      +materialized: ephemeral   # or view; table only when reused heavily
      +schema: intermediate
    marts:
      +materialized: table
      +schema: marts
      +contract: {enforced: true}
```

Check that `persist_docs` and contracts are supported by your adapter before
enabling them.
