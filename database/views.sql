USE DataReliabilityDB;
GO

CREATE OR ALTER VIEW dbo.vw_analysis_summary AS
SELECT
    ar.run_id, d.dataset_id, d.dataset_name, d.source_type, d.row_count,
    ar.started_at, ar.completed_at, ar.status, ar.overall_score,
    COUNT(rm.metric_id) AS available_metric_count
FROM dbo.analysis_runs ar
JOIN dbo.datasets d ON d.dataset_id = ar.dataset_id
LEFT JOIN dbo.reliability_metrics rm ON rm.run_id = ar.run_id AND rm.metric_value IS NOT NULL
GROUP BY ar.run_id, d.dataset_id, d.dataset_name, d.source_type, d.row_count,
         ar.started_at, ar.completed_at, ar.status, ar.overall_score;
GO

CREATE OR ALTER VIEW dbo.vw_context_risk AS
SELECT cr.run_id, d.dataset_name, cr.context_column, cr.context_value,
       cr.reliability_score, cr.sample_size, cr.sufficient_sample,
       RANK() OVER (PARTITION BY cr.run_id, cr.context_column ORDER BY cr.reliability_score) AS risk_rank
FROM dbo.context_results cr
JOIN dbo.analysis_runs ar ON ar.run_id = cr.run_id
JOIN dbo.datasets d ON d.dataset_id = ar.dataset_id;
GO
