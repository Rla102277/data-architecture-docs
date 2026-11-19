# Example brief: Northwind Distribution (fictional)

A worked example of the kickoff brief and the start of the doc set. The company,
people and numbers are invented. It shows the facts file, a filled executive
brief and a CIO reader review, so you can see the altitude and the consistency
the skill aims for. It covers the executive pack only; run the plugin on a real project to get all three packs.

- **Project / code:** Atlas / atl
- **Decision this makes clearer:** which customers and SKUs to reprice before the
  annual contract renewals, for the VP of Sales and the CFO
- **Single action:** Approve $180K and a two-person team by Jan 15 so margin by
  customer and SKU is ready for the April renewal cycle.
- **Sponsor:** CFO, judged on gross margin
- **Consumers:** Finance (8), Sales leadership (12), Ops planning (6)
- **Phase 1:** ERP (orders, invoices, cost), WMS (shipments), CRM (accounts);
  margin by customer and SKU, daily. Out: forecasting, ML, real time.
- **Sources:** ERP on SQL Server (change tracking available), WMS nightly CSV to
  SFTP, CRM SaaS API. ERP and CRM hold PII (contacts) and SOX-relevant financials.
- **Platform:** not chosen. Microsoft 365 E5 and Power BI Pro already owned.
- **Team:** one data engineer, one BI analyst, plus one contract engineer for 6 months
- **NFRs:** data by 06:00 Central on business days; 7 years of history; RPO 24h, RTO 8h
- **Falsifier:** if margin by customer cannot be reconciled to the GL within 0.5%
  by end of February, stop and fix cost allocation before building more.
