CREATE VIEW rpt.vSalesByCustomer AS
WITH x AS (SELECT CustomerKey, SUM(Amount) AS Amt FROM dw.FactSales GROUP BY CustomerKey)
SELECT c.CustomerName, x.Amt FROM x JOIN dw.DimCustomer c ON c.CustomerKey = x.CustomerKey;
