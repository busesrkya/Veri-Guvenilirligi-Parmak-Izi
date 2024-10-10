from __future__ import annotations

import json

import pandas as pd


class AnalysisRepository:
    def __init__(self, connection):
        self.connection = connection

    def save_analysis(self, dataset_name: str, source_type: str, result: dict) -> int:
        cursor = self.connection.cursor()
        profile = result["profile"]
        cursor.execute(
            """
            INSERT INTO dbo.datasets(dataset_name, source_type, row_count, column_count)
            OUTPUT INSERTED.dataset_id VALUES (?, ?, ?, ?)
            """,
            dataset_name,
            source_type,
            profile["row_count"],
            profile["column_count"],
        )
        dataset_id = int(cursor.fetchone()[0])
        cursor.execute(
            """
            INSERT INTO dbo.analysis_runs(dataset_id, status, overall_score, completed_at)
            OUTPUT INSERTED.run_id VALUES (?, 'completed', ?, SYSUTCDATETIME())
            """,
            dataset_id,
            result["overall_score"],
        )
        run_id = int(cursor.fetchone()[0])
        for name, value in result["metrics"].items():
            cursor.execute(
                "INSERT INTO dbo.reliability_metrics(run_id, metric_name, metric_value, calculation_details) VALUES (?, ?, ?, ?)",
                run_id,
                name,
                value,
                json.dumps(result["metric_details"][name], default=str),
            )
        for row in result["context_results"].to_dict("records"):
            cursor.execute(
                """
                INSERT INTO dbo.context_results
                (run_id, context_column, context_value, reliability_score, sample_size, sufficient_sample)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                run_id,
                row["context_column"],
                row["context_value"],
                row["reliability_score"],
                row["sample_size"],
                row["sufficient_sample"],
            )
        for row in result["temporal_results"].to_dict("records"):
            for metric_name in ("completeness", "validity", "reliability_score"):
                value = row.get(metric_name)
                cursor.execute(
                    """
                    INSERT INTO dbo.temporal_metrics(run_id, period_start, period_end, metric_name, metric_value)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    run_id,
                    row["period_start"],
                    row["period_end"],
                    metric_name,
                    None if pd.isna(value) else value,
                )
        for row in result["detected_issues"].to_dict("records"):
            cursor.execute(
                """
                INSERT INTO dbo.detected_issues
                (run_id, issue_type, column_name, context_column, context_value, issue_count, description)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                run_id, row["issue_type"], row.get("column_name"), row.get("context_column"),
                row.get("context_value"), row["issue_count"], row.get("description"),
            )
        self.connection.commit()
        return run_id

    def save_experiments(self, run_id: int, experiments: pd.DataFrame) -> None:
        cursor = self.connection.cursor()
        for row in experiments.to_dict("records"):
            cursor.execute(
                """
                INSERT INTO dbo.model_experiments
                (run_id, model_name, experiment_type, accuracy, precision_score, recall_score,
                 f1_score, confusion_matrix, random_seed, reliability_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                run_id, row["model"], row["scenario"], row["accuracy"], row["precision"],
                row["recall"], row["f1_score"], row["confusion_matrix"], row["random_seed"],
                row["reliability_score"],
            )
        self.connection.commit()

    def analysis_history(self) -> pd.DataFrame:
        return pd.read_sql_query(
            """
            SELECT ar.run_id, d.dataset_name, ar.started_at, ar.completed_at, ar.status, ar.overall_score
            FROM dbo.analysis_runs ar JOIN dbo.datasets d ON d.dataset_id = ar.dataset_id
            ORDER BY ar.started_at DESC
            """,
            self.connection,
        )
