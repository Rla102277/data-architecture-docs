-- revenue by customer for last month
SELECT c.CustomerName, SUM(l.Amount) AS Revenue, AVG(o.DiscountPct) AS AvgDiscount
FROM sales.Orders o WITH (NOLOCK)
JOIN sales.OrderLines l ON l.OrderID = o.OrderID
LEFT JOIN sales.Customers c ON c.CustomerID = o.CustomerID
LEFT JOIN sales.Payments p ON p.OrderID = o.OrderID
WHERE o.OrderDate BETWEEN '2026-10-01' AND '2026-10-31 23:59:59'
  AND c.Segment = 'Retail'
  AND o.CustomerID NOT IN (SELECT CustomerID FROM sales.InternalAccounts)
GROUP BY c.CustomerName
