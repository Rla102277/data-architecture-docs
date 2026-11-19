CREATE PROCEDURE dbo.usp_LoadSales @RunDate date AS
BEGIN
  SET NOCOUNT ON;
  IF OBJECT_ID('tempdb..#stage') IS NOT NULL DROP TABLE #stage;
  SELECT o.OrderID, o.CustomerID, l.Amount
  INTO #stage
  FROM src.Orders o WITH (NOLOCK)
  JOIN src.OrderLines l ON l.OrderID = o.OrderID
  WHERE o.OrderDate = @RunDate;

  MERGE dw.FactSales AS t
  USING (SELECT s.OrderID, c.CustomerKey, s.Amount FROM #stage s JOIN dw.DimCustomer c ON c.CustomerID = s.CustomerID) AS s
  ON t.OrderID = s.OrderID
  WHEN MATCHED THEN UPDATE SET t.Amount = s.Amount
  WHEN NOT MATCHED THEN INSERT (OrderID, CustomerKey, Amount) VALUES (s.OrderID, s.CustomerKey, s.Amount);

  DECLARE @sql nvarchar(max) = N'DELETE FROM dw.Audit WHERE 1=0';
  EXEC sp_executesql @sql;
END
GO
CREATE PROCEDURE dbo.usp_Nightly AS
BEGIN
  BEGIN TRY
    EXEC dbo.usp_LoadSales @RunDate = '2026-01-01';
    INSERT INTO dw.Audit (RunAt, Status)
    SELECT GETDATE(), CASE WHEN 1=1 THEN 'OK' ELSE 'X' END;
    UPDATE f SET f.Amount = 0 FROM dw.FactSales f JOIN src.Refunds r ON r.OrderID = f.OrderID;
  END TRY
  BEGIN CATCH
    INSERT INTO dw.ErrorLog (Msg) VALUES (ERROR_MESSAGE());
  END CATCH
END
