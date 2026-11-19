-- Control and audit tables for incremental pipelines (T-SQL; adapt types for Snowflake/Spark).

CREATE TABLE ctl.watermark (
    pipeline_name     varchar(200)  NOT NULL,
    source_object     varchar(400)  NOT NULL,
    watermark_type    varchar(30)   NOT NULL,   -- timestamp | ct_version | lsn | cursor
    watermark_value   varchar(200)  NOT NULL,   -- stored as text, typed by watermark_type
    last_batch_id     varchar(100)  NOT NULL,
    updated_at_utc    datetime2(3)  NOT NULL,
    CONSTRAINT pk_watermark PRIMARY KEY (pipeline_name, source_object)
);

CREATE TABLE ctl.batch_audit (
    batch_id          varchar(100)  NOT NULL,
    pipeline_name     varchar(200)  NOT NULL,
    source_object     varchar(400)  NOT NULL,
    started_at_utc    datetime2(3)  NOT NULL,
    ended_at_utc      datetime2(3)  NULL,
    status            varchar(20)   NOT NULL,   -- running | succeeded | failed
    watermark_from    varchar(200)  NULL,
    watermark_to      varchar(200)  NULL,
    rows_extracted    bigint        NULL,
    rows_landed       bigint        NULL,
    error_message     nvarchar(4000) NULL,
    CONSTRAINT pk_batch_audit PRIMARY KEY (batch_id, source_object)
);

-- Advance the watermark only after the landed rows are committed and counted:
-- BEGIN TRAN;
--   UPDATE ctl.batch_audit SET status = 'succeeded', ended_at_utc = SYSUTCDATETIME(), rows_landed = @rows WHERE ...;
--   UPDATE ctl.watermark SET watermark_value = @new_value, last_batch_id = @batch_id, updated_at_utc = SYSUTCDATETIME() WHERE ...;
-- COMMIT;
-- Every caught error must set status = 'failed' AND re-raise, so the orchestrator sees the failure.
