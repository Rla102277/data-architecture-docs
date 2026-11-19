# Discovery Question Bank

Ask in batches of at most 6. Always offer a default in brackets so the user can
answer "defaults". Skip anything the repo scan already answered.

## Batch 1: Why and who
1. What business problem does this solve, in one sentence? [none, required]
2. Who is the executive sponsor, and what outcome will they be judged on? [CIO; "one trusted source for operational reporting"]
3. Who are the primary consumers (teams, roles, count)? [Finance, Ops, Sales leadership; ~50 report users]
4. What is in scope for phase 1, and what is explicitly out? [3-5 core sources, core reporting; no ML, no real-time]
5. Hard deadline or forcing event (audit, contract end, system migration)? [none]
6. How will we know it worked (2-3 measurable KPIs)? [report build time, data freshness, number of manual spreadsheets retired]

## Batch 2: Sources
1. List source systems: name, type (ERP, CRM, DB, SaaS API, files), owner. [required]
2. For each: rough row volume and daily change volume. [unknown, estimate later]
3. Access method available: direct DB, CDC/change tracking, API, export files, vendor share. [direct DB read replica]
4. Any source that is being replaced or migrated soon? [none]
5. Any PII, PHI, PCI, or financially material data? [PII yes, SOX-relevant financials yes]
6. Who can answer questions about each source's data meaning? [source system owner]

## Batch 3: Platform and constraints
1. Target platform already chosen? (Fabric, Snowflake, Databricks, Synapse, BigQuery, Redshift) [ask; do not default]
2. Cloud and region; any data residency rules? [Azure, US region]
3. Existing tools we must use or integrate (dbt, Airflow, Power BI, Tableau, Purview, Fivetran)? [Power BI, Git]
4. Identity provider and access model (Entra ID groups, SSO)? [Entra ID security groups]
5. Budget envelope (one-time and annual)? [unknown, model it]
6. Licensing already owned (Fabric capacity SKU, Snowflake credits, E5)? [unknown]

## Batch 4: Non-functional requirements
1. Freshness: how current must data be for the main use case? [daily by 06:00 local]
2. Availability: what happens to the business if the platform is down for a day? [reports stale, low impact]
3. History: how far back, and do we need point-in-time ("as was") reporting? [7 years, yes for financials]
4. Recovery: acceptable data loss (RPO) and downtime (RTO)? [RPO 24h, RTO 8h]
5. Scale in 3 years: users, sources, data volume? [3x]
6. Compliance frameworks: SOX, HIPAA, GDPR, CCPA, SOC 2? [SOX, CCPA]

## Batch 5: Team and operations
1. Team today: roles and headcount (DE, analytics engineer, BI, architect)? [required]
2. Planned hires or contractors? [none]
3. Who supports it in production, and what hours? [team, business hours, best-effort after]
4. Ticketing and incident tooling (ServiceNow, Jira, Teams, PagerDuty)? [Jira + Teams]
5. Branching and release style today? [trunk-based, PR review]
6. Definition of done the team already uses? [none, propose one]

## Batch 6: Modeling and consumption
1. Preferred modeling style: Kimball star, Data Vault 2.0 + marts, OBT, or no preference? [raw vault or bronze history + Kimball gold]
2. Key business entities and conformed dimensions (customer, product, location, date, employee)? [ask]
3. Key metrics with agreed definitions? Where do they live today? [spreadsheets; propose metric catalog]
4. Semantic layer: one shared model or per-domain? [shared core + domain extensions]
5. Self-service expectations: who builds their own reports? [analysts in Finance and Ops]
6. Any ML, reverse ETL, or data sharing to partners? [not in phase 1]
