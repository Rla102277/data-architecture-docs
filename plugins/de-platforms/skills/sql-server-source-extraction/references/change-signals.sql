-- SQL Server change signals. Run on the source (or readable secondary) with an extract login.

-- A) rowversion watermark
-- Store the next lower bound per table (binary(8)) in the control table. Lower bound inclusive, upper bound exclusive.
DECLARE @from_rv binary(8) = 0x0000000000000000;      -- from control table
DECLARE @to_rv   binary(8) = MIN_ACTIVE_ROWVERSION();  -- exclusive upper bound: skips rows of still-open transactions
SELECT OrderID, CustomerID, Amount, RowVer
FROM dbo.Orders
WHERE RowVer >= @from_rv AND RowVer < @to_rv;
-- after a committed load: control.watermark = @to_rv  (this run's exclusive upper bound is the next run's inclusive lower bound)

-- B) change tracking (net changes and deletes)
DECLARE @last_version bigint = 0;   -- from control table
IF @last_version < CHANGE_TRACKING_MIN_VALID_VERSION(OBJECT_ID('dbo.Orders'))
    THROW 50001, 'Stored change tracking version is too old: full resync required', 1;

DECLARE @current_version bigint = CHANGE_TRACKING_CURRENT_VERSION();
SELECT ct.SYS_CHANGE_OPERATION, ct.OrderID, o.CustomerID, o.Amount
FROM CHANGETABLE(CHANGES dbo.Orders, @last_version) AS ct
LEFT JOIN dbo.Orders AS o ON o.OrderID = ct.OrderID;   -- deleted rows come back with NULL columns, operation 'D'
-- after a committed load: control.watermark = @current_version
-- Run the read and the version capture under snapshot isolation for consistency.

-- C) CDC (all changes)
DECLARE @from_lsn binary(10) = sys.fn_cdc_get_min_lsn('dbo_Orders');  -- or the stored LSN + 1 via sys.fn_cdc_increment_lsn
DECLARE @to_lsn   binary(10) = sys.fn_cdc_get_max_lsn();
SELECT __$operation, __$start_lsn, OrderID, CustomerID, Amount
FROM cdc.fn_cdc_get_all_changes_dbo_Orders(@from_lsn, @to_lsn, N'all');
-- __$operation: 1 delete, 2 insert, 3 update (before), 4 update (after)
-- Monitor: SELECT * FROM sys.dm_cdc_log_scan_sessions; retention in msdb.dbo.cdc_jobs (cleanup job)
