USE DataReliabilityDB;
GO

CREATE OR ALTER PROCEDURE dbo.usp_GetDatasetReliabilityTrend
    @DatasetId BIGINT
AS
BEGIN
    SET NOCOUNT ON;
    WITH ordered_runs AS (
        SELECT run_id, started_at, overall_score,
               LAG(overall_score) OVER (ORDER BY started_at) AS previous_score
        FROM dbo.analysis_runs
        WHERE dataset_id = @DatasetId AND status = 'completed'
    )
    SELECT run_id, started_at, overall_score, previous_score,
           overall_score - previous_score AS change_from_previous
    FROM ordered_runs ORDER BY started_at;
END;
GO

CREATE OR ALTER PROCEDURE dbo.usp_GetWorstContexts
    @RunId BIGINT,
    @ContextColumn NVARCHAR(128) = NULL,
    @MinimumSampleSize INT = 30,
    @TopN INT = 10
AS
BEGIN
    SET NOCOUNT ON;
    SELECT TOP (@TopN) context_column, context_value, reliability_score, sample_size
    FROM dbo.context_results
    WHERE run_id = @RunId
      AND sample_size >= @MinimumSampleSize
      AND (@ContextColumn IS NULL OR context_column = @ContextColumn)
    ORDER BY reliability_score, sample_size DESC;
END;
GO

CREATE OR ALTER PROCEDURE dbo.usp_GetIncreasingIssues
    @DatasetId BIGINT
AS
BEGIN
    SET NOCOUNT ON;
    WITH issue_by_run AS (
        SELECT ar.run_id, ar.started_at, di.issue_type, SUM(di.issue_count) AS issue_count
        FROM dbo.analysis_runs ar
        JOIN dbo.detected_issues di ON di.run_id = ar.run_id
        WHERE ar.dataset_id = @DatasetId
        GROUP BY ar.run_id, ar.started_at, di.issue_type
    ), changes AS (
        SELECT *, issue_count - LAG(issue_count) OVER
            (PARTITION BY issue_type ORDER BY started_at) AS issue_change
        FROM issue_by_run
    )
    SELECT issue_type, run_id, started_at, issue_count, issue_change
    FROM changes WHERE issue_change > 0
    ORDER BY issue_change DESC;
END;
GO
