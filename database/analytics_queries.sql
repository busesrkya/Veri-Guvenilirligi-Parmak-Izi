USE DataReliabilityDB;
GO

-- 1. Tamamlanan analizler içinde en düşük güvenilirlik skoruna sahip veri seti.
SELECT TOP (1) d.dataset_name, ar.run_id, ar.overall_score, ar.completed_at
FROM dbo.analysis_runs ar JOIN dbo.datasets d ON d.dataset_id = ar.dataset_id
WHERE ar.status = 'completed' AND ar.overall_score IS NOT NULL
ORDER BY ar.overall_score, ar.completed_at DESC;

-- 2. En fazla kayıtlı veri problemi oluşturan makine.
SELECT TOP (10) context_value AS machine_id, SUM(issue_count) AS total_issues
FROM dbo.detected_issues
WHERE context_column = 'machine_id'
GROUP BY context_value
HAVING SUM(issue_count) > 0
ORDER BY total_issues DESC;

-- 3. Güvenilirliği en düşük vardiya.
SELECT context_value AS shift, AVG(reliability_score) AS average_reliability, SUM(sample_size) AS observations
FROM dbo.context_results
WHERE context_column = 'shift' AND sufficient_sample = 1
GROUP BY context_value
ORDER BY average_reliability;

-- 4. Önceki analize göre değişim (window function).
WITH run_changes AS (
    SELECT d.dataset_name, ar.run_id, ar.started_at, ar.overall_score,
           LAG(ar.overall_score) OVER (PARTITION BY ar.dataset_id ORDER BY ar.started_at) AS previous_score
    FROM dbo.analysis_runs ar JOIN dbo.datasets d ON d.dataset_id = ar.dataset_id
    WHERE ar.status = 'completed'
)
SELECT *, overall_score - previous_score AS score_change FROM run_changes ORDER BY started_at DESC;

-- 5. En fazla problem görülen sensörler (alt sorgu her veri setinin son çalışmasını bulur).
SELECT di.context_value AS sensor_id, SUM(di.issue_count) AS total_issues
FROM dbo.detected_issues di
WHERE di.context_column = 'sensor_id'
  AND di.run_id IN (SELECT MAX(run_id) FROM dbo.analysis_runs GROUP BY dataset_id)
GROUP BY di.context_value ORDER BY total_issues DESC;

-- 6. Ardışık çalışmalarda artış gösteren problemler.
WITH issue_counts AS (
    SELECT ar.started_at, di.issue_type, SUM(di.issue_count) AS issue_count
    FROM dbo.detected_issues di JOIN dbo.analysis_runs ar ON ar.run_id = di.run_id
    GROUP BY ar.started_at, di.issue_type
), compared AS (
    SELECT *, LAG(issue_count) OVER (PARTITION BY issue_type ORDER BY started_at) AS previous_count
    FROM issue_counts
)
SELECT *, issue_count - previous_count AS increase FROM compared
WHERE issue_count > previous_count ORDER BY increase DESC;

-- 7. Eksik değer sayısının yükseldiği bağlamlar.
SELECT context_column, context_value, SUM(issue_count) AS missing_values
FROM dbo.detected_issues
WHERE issue_type LIKE '%missing%'
GROUP BY context_column, context_value
HAVING SUM(issue_count) >= 10
ORDER BY missing_values DESC;

-- 8. Model performansının daha düşük olduğu analizler.
SELECT ar.run_id, d.dataset_name, me.experiment_type, me.model_name,
       me.reliability_score, me.f1_score,
       ROW_NUMBER() OVER (PARTITION BY ar.run_id ORDER BY me.f1_score) AS performance_rank
FROM dbo.model_experiments me
JOIN dbo.analysis_runs ar ON ar.run_id = me.run_id
JOIN dbo.datasets d ON d.dataset_id = ar.dataset_id
WHERE me.f1_score IS NOT NULL
ORDER BY me.f1_score;

-- CASE WHEN örneği: operasyonel risk bandı.
SELECT run_id, overall_score,
       CASE WHEN overall_score < 70 THEN 'high risk'
            WHEN overall_score < 85 THEN 'review'
            ELSE 'stable' END AS reliability_band
FROM dbo.analysis_runs WHERE status = 'completed';
GO
