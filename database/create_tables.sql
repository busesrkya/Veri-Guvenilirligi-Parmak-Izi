USE DataReliabilityDB;
GO

CREATE TABLE dbo.datasets (
    dataset_id BIGINT IDENTITY(1,1) PRIMARY KEY,
    dataset_name NVARCHAR(200) NOT NULL,
    source_type NVARCHAR(40) NOT NULL,
    row_count BIGINT NOT NULL CHECK (row_count >= 0),
    column_count INT NOT NULL CHECK (column_count >= 0),
    created_at DATETIME2(3) NOT NULL CONSTRAINT DF_datasets_created DEFAULT SYSUTCDATETIME()
);

CREATE TABLE dbo.analysis_runs (
    run_id BIGINT IDENTITY(1,1) PRIMARY KEY,
    dataset_id BIGINT NOT NULL,
    started_at DATETIME2(3) NOT NULL CONSTRAINT DF_runs_started DEFAULT SYSUTCDATETIME(),
    completed_at DATETIME2(3) NULL,
    status VARCHAR(20) NOT NULL CONSTRAINT DF_runs_status DEFAULT 'running',
    overall_score DECIMAL(6,3) NULL,
    CONSTRAINT CK_runs_status CHECK (status IN ('running', 'completed', 'failed')),
    CONSTRAINT CK_runs_score CHECK (overall_score IS NULL OR overall_score BETWEEN 0 AND 100),
    CONSTRAINT FK_runs_dataset FOREIGN KEY (dataset_id) REFERENCES dbo.datasets(dataset_id)
);

CREATE TABLE dbo.reliability_metrics (
    metric_id BIGINT IDENTITY(1,1) PRIMARY KEY,
    run_id BIGINT NOT NULL,
    metric_name VARCHAR(60) NOT NULL,
    metric_value DECIMAL(8,4) NULL,
    calculation_details NVARCHAR(MAX) NULL,
    CONSTRAINT UQ_metrics_run_name UNIQUE (run_id, metric_name),
    CONSTRAINT CK_metrics_value CHECK (metric_value IS NULL OR metric_value BETWEEN 0 AND 100),
    CONSTRAINT FK_metrics_run FOREIGN KEY (run_id) REFERENCES dbo.analysis_runs(run_id) ON DELETE CASCADE
);

CREATE TABLE dbo.context_results (
    context_id BIGINT IDENTITY(1,1) PRIMARY KEY,
    run_id BIGINT NOT NULL,
    context_column NVARCHAR(128) NOT NULL,
    context_value NVARCHAR(400) NOT NULL,
    reliability_score DECIMAL(8,4) NULL,
    sample_size BIGINT NOT NULL,
    sufficient_sample BIT NOT NULL,
    CONSTRAINT FK_context_run FOREIGN KEY (run_id) REFERENCES dbo.analysis_runs(run_id) ON DELETE CASCADE
);

CREATE TABLE dbo.detected_issues (
    issue_id BIGINT IDENTITY(1,1) PRIMARY KEY,
    run_id BIGINT NOT NULL,
    issue_type NVARCHAR(80) NOT NULL,
    column_name NVARCHAR(128) NULL,
    context_column NVARCHAR(128) NULL,
    context_value NVARCHAR(400) NULL,
    issue_count BIGINT NOT NULL CHECK (issue_count >= 0),
    description NVARCHAR(1000) NULL,
    CONSTRAINT FK_issues_run FOREIGN KEY (run_id) REFERENCES dbo.analysis_runs(run_id) ON DELETE CASCADE
);

CREATE TABLE dbo.model_experiments (
    experiment_id BIGINT IDENTITY(1,1) PRIMARY KEY,
    run_id BIGINT NOT NULL,
    model_name NVARCHAR(100) NOT NULL,
    experiment_type NVARCHAR(100) NOT NULL,
    accuracy DECIMAL(8,6) NULL,
    precision_score DECIMAL(8,6) NULL,
    recall_score DECIMAL(8,6) NULL,
    f1_score DECIMAL(8,6) NULL,
    confusion_matrix NVARCHAR(500) NULL,
    random_seed INT NOT NULL,
    reliability_score DECIMAL(8,4) NULL,
    created_at DATETIME2(3) NOT NULL CONSTRAINT DF_experiments_created DEFAULT SYSUTCDATETIME(),
    CONSTRAINT FK_experiments_run FOREIGN KEY (run_id) REFERENCES dbo.analysis_runs(run_id) ON DELETE CASCADE
);

CREATE TABLE dbo.temporal_metrics (
    temporal_metric_id BIGINT IDENTITY(1,1) PRIMARY KEY,
    run_id BIGINT NOT NULL,
    period_start DATETIME2(3) NOT NULL,
    period_end DATETIME2(3) NOT NULL,
    metric_name VARCHAR(60) NOT NULL,
    metric_value DECIMAL(8,4) NULL,
    CONSTRAINT UQ_temporal UNIQUE (run_id, period_start, metric_name),
    CONSTRAINT FK_temporal_run FOREIGN KEY (run_id) REFERENCES dbo.analysis_runs(run_id) ON DELETE CASCADE
);

CREATE INDEX IX_runs_dataset_started ON dbo.analysis_runs(dataset_id, started_at DESC);
CREATE INDEX IX_context_run_column_score ON dbo.context_results(run_id, context_column, reliability_score);
CREATE INDEX IX_issues_run_type ON dbo.detected_issues(run_id, issue_type);
CREATE INDEX IX_temporal_run_metric_period ON dbo.temporal_metrics(run_id, metric_name, period_start);
CREATE INDEX IX_experiments_run_f1 ON dbo.model_experiments(run_id, f1_score);
GO
