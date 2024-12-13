# Data Reliability Fingerprint

[Türkçe](#türkçe) · [English](#english)

---

# Türkçe

## Projeye Genel Bakış

Data Reliability Fingerprint, bir veri setinin hangi bölümlerde, zamanlarda ve çalışma koşullarında güvenilirliğinin düştüğünü inceleyen Python, Microsoft SQL Server ve Streamlit projesidir. Uygulama yalnızca genel eksik değer veya tekrar sayısı vermek yerine açıklanabilir güvenilirlik bileşenlerini bağlam ve zaman içinde karşılaştırır; ardından kontrollü veri bozulmasının sınıflandırma modelleriyle ilişkisini ölçer.

## Araştırma Sorusu

> Bir veri seti her koşulda aynı ölçüde güvenilir midir? Güvenilirlik nerede, ne zaman ve hangi çalışma bağlamlarında düşer; bu düşüş makine öğrenmesi performansıyla nasıl ilişkilidir?

Genel skor, karşılaştırmayı kolaylaştıran bir uygulama varsayımıdır. Evrensel veya bilimsel olarak doğrulanmış bir veri kalitesi ölçüsü olarak sunulmaz.

## Motivasyon

Genel %3 eksik veri oranı, belirli bir makinenin gece vardiyasında oluşan %20'lik problemi gizleyebilir. Eksiklik, gürültü ve bağlama özgü bozulmalar aynı genel kalite skoruna yakın görünse bile modeli farklı etkileyebilir. Bu nedenle proje; bileşen skorlarını, bağlam tablolarını, zamansal eğilimleri, model metriklerini ve varsayımları ayrı ayrı saklar.

## Özellikler

- Altı bileşenli, açıklanabilir güvenilirlik parmak izi
- Hesaplanamayan metrikler için `None / Hesaplanamadı` davranışı; otomatik 100 ataması yapılmaz
- Kullanıcının seçtiği kolonlarda örneklem yeterliliği, güven aralığı ve çoklu karşılaştırma bilgisi içeren bağlam analizi
- Veri zaman aralığına göre günlük, haftalık veya aylık zamansal analiz
- Aralık doğrulaması, tekrar tespiti, dayanıklı aykırı değer, korelasyon, hareketli istatistik ve regresyon residual analizi
- Bağlama özgü ve zamansal hatalar içeren yeniden üretilebilir endüstriyel sensör veri üreticisi
- Eksiklik, sensör gürültüsü ve gece vardiyası bozulması altında Logistic Regression ve Random Forest deneyleri
- Zaman sıralı train/test ayrımı ve yalnızca eğitim verisinde öğrenilen scikit-learn pipeline'ları
- CSV yükleme destekli, altı sayfalı Türkçe Streamlit dashboard'u
- SQL Server analiz geçmişi, metrik, bağlam, zaman, sorun ve model deney tabloları
- JOIN, GROUP BY, HAVING, CASE, CTE, alt sorgu, `LAG`, `ROW_NUMBER`, view ve stored procedure örnekleri
- Sayısal sonuçları, uç durumları ve veri sızıntısını denetleyen pytest testleri

## Teknoloji Yığını

Python 3.11+, pandas, NumPy, SciPy, scikit-learn, Matplotlib, Seaborn, Plotly, Streamlit, pyodbc, python-dotenv, pytest, Microsoft SQL Server ve T-SQL.

## Veri Seti

`data/generate_dataset.py`, varsayılan olarak 36.000 temiz temel gözlem üretir ve bu gözlemlerin bir kopyasına kontrollü sorunlar ekler. Makine yükü, hız, titreşim, sıcaklık ve basınç birbiriyle ilişkili fakat deterministik değildir. Farklı makine ve çalışma durumları farklı dağılımlara sahiptir.

Eklenen sorunlar; rastgele eksiklik, M09/gece vardiyası titreşim eksikliği, geçersiz nem değerleri, titreşim sıçramaları, M04 basınç tutarsızlığı, son dönemde sıcaklık kayması ve tekrarlanan kayıtlardır. Gözlenen CSV'de hata etiketi bulunmaz. `synthetic_error_reference.csv` yalnızca bağımsız değerlendirme içindir; analizde veya model özelliklerinde kullanılmaz ve varsayılan olarak Git dışında tutulur.

Gerçek veri yolu için [UCI MetroPT-3](https://archive.ics.uci.edu/dataset/791/metropt%2B3%2Bdataset) veri setine yönelik kolon eşleme ve lisans notları [gerçek veri rehberinde](docs/real_dataset_guide.md) bulunur. Harici veri projeye eklenmemiş ve bu veri üzerinde sonuç üretilmiş gibi davranılmamıştır.

## Güvenilirlik Parmak İzi Metodolojisi

Tüm bileşenler 0–100 aralığındadır. Bir bileşenin ön koşulları yoksa değer `None` olur ve 100 kabul edilmez.

| Bileşen | Tanım | Temel sınırlama |
|---|---|---|
| Completeness | `100 × (1 − eksik hücre / toplam hücre)` | Tüm hücreleri eşit önemli kabul eder |
| Validity | Kurallara uyan gözlenen değer oranı | Aralık kuralları alan varsayımıdır |
| Consistency | Dayanıklı aykırı değer, regresyon residual'ı ve ilişki sapması cezaları | Tutarsızlık kesin arıza teşhisi değildir |
| Uniqueness | `100 × (1 − tekrar kayıt / kayıt)` | Sonuç anahtar seçimine bağlıdır |
| Context Stability | `max(0, 100 − 3 × uygun grup skorlarının ağırlıklı std değeri)` | Gruplar örtüşebilir ve çoklu karşılaştırma riski vardır |
| Temporal Stability | `max(0, 100 − 2,5 × dönem std − pozitif kötüleşme)` | Dönem toplulaştırması kısa olayları gizleyebilir |

Varsayılan genel skor, hesaplanabilen bileşenlerin eşit ağırlıklı ortalamasıdır. Kullanılan ağırlıklar yeniden normalize edilir; kullanılan ve hesaplanamayan metrikler sonuçta ayrıca saklanır. Ayrıntılı formüller [metodoloji belgesindedir](docs/methodology.md).

## Bağlama Duyarlı Analiz

Seçilen her bağlam kolonu bağımsız gruplandırılır. Grup skoru uygulanabilen completeness, validity ve uniqueness bileşenlerinin ortalamasıdır. 30'dan az kaydı olan gruplar yetersiz olarak işaretlenir ve context stability hesabına katılmaz. Çıktı, completeness güven aralığı ve keşif amaçlı Bonferroni düzeltilmiş alfa değerini içerir; her farkı istatistiksel olarak kesin kabul etmez.

## Zamansal Analiz

Sistem yedi güne kadar günlük, 120 güne kadar haftalık, daha uzun sürelerde aylık dönemler seçer. Her dönemde completeness, validity ve uygulanabilen bileşenlerin ortalaması raporlanır. Geçerli zaman damgası yoksa yalnızca zamansal bileşen hesaplanamaz; diğer analizler devam eder.

## Makine Öğrenmesi Deneyleri

Veri zaman damgasına göre sıralanır; ilk %75 eğitim, sonraki %25 test olarak kullanılır. Sayısal medyan doldurma ve ölçekleme ile kategorik mod doldurma ve one-hot encoding adımları pipeline içinde yalnızca eğitim verisine fit edilir.

Logistic Regression ve Random Forest şu senaryolarda karşılaştırılır:

1. gözlenen temel veri;
2. sayısal hücrelerde %10 eksiklik;
3. orta seviyede Gauss sensör gürültüsü;
4. gece vardiyasına özgü titreşim ve basınç eksikliği.

Accuracy, macro precision, macro recall, macro F1, confusion matrix, random seed, eğitim/test boyutları ve senaryo güvenilirlik skoru kaydedilir. Sentetik hata işaretleri modele verilmez.

## Veritabanı Mimarisi

İlişkisel şema `datasets` tablosunu tekrarlanabilir `analysis_runs` kayıtlarına bağlar. Bileşen metrikleri, bağlam sonuçları, tespit edilen sorunlar, zamansal değerler ve model deneyleri analiz çalışmasına bağlıdır. Foreign key, check, unique constraint ve sorgu odaklı indexler kullanılır. Ayrıntılar [veritabanı tasarımında](docs/database_design.md) bulunur.

## Kurulum

```powershell
git clone <depo-adresi>
cd data-reliability-fingerprint
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

SQL Server'a kayıt yapılacaksa Windows için Microsoft ODBC Driver 18 ayrıca kurulmalıdır. Çalışan bir SQL Server olmadan Python analizleri kullanılabilir.

## Yapılandırma

```powershell
Copy-Item .env.example .env
```

Varsayılan yapılandırma Windows Authentication kullanır. SQL Server Authentication için `DB_USERNAME` ve `DB_PASSWORD` birlikte ayarlanmalıdır. `.env` dosyasını Git'e eklemeyin.

## Kullanım

```powershell
# Sentetik veriyi üret
python data/generate_dataset.py

# Parmak izi ve ML deneylerini çalıştır
python -m src.main data/sample_data.csv --name industrial_sensor_data --ml

# Sözdizimi ve test kontrolü
python -m compileall src dashboard data tests
python -m pytest -q
```

Raporlar `reports/fingerprint.json`, `context_results.csv`, `temporal_results.csv`, `detected_issues.csv` ve ML seçeneği kullanıldığında `ml_experiments.csv` dosyalarına yazılır.

## Dashboard

```powershell
python -m streamlit run dashboard/app.py
```

Dashboard; Genel Bakış, Veri Profilleme, Bağlam Analizi, Zamansal Analiz, ML Deneyleri ve Analiz Geçmişi sayfalarından oluşur. SQL Server bağlantısı yoksa anlaşılır hata gösterilir ve hiçbir sonuç kaydedilmiş gibi sunulmaz.

## Microsoft SQL Server Kurulumu

SQL Server Management Studio'da sırasıyla çalıştırın:

1. `database/create_database.sql`
2. `database/create_tables.sql`
3. `database/views.sql`
4. `database/stored_procedures.sql`
5. Örnek rapor sorguları için `database/analytics_queries.sql`

Ardından `.env.example` dosyasını `.env` olarak kopyalayın, sunucu/driver değerlerini düzenleyin ve dashboard'daki Analiz Geçmişi sayfasından bağlantıyı doğrulayın. Python tarafında değerler parametreli `?` placeholder'larıyla gönderilir.

## Deney Sonuçları

Üretilen 36.216 satırlık veri üzerinde fingerprint analizi çalıştırılmıştır: genel skor **99,6635**; completeness 99,7901; validity 99,8451; consistency 99,3249; uniqueness 99,4036; context stability 99,6754 ve temporal stability 99,9422 olarak ölçülmüştür. Bu yüksek genel skor, yerel ve bağlama özgü sorunların olmadığı anlamına gelmez; örneğin M09 makinesinin grup skoru diğer büyük gruplara göre daha düşüktür.

Bu bilgisayarın Windows Application Control ilkesi scikit-learn native DLL'lerini engellediği için sayısal ML sonuçları üretilememiştir. Başarı değeri uydurulmamış; deney kodu ve testleri teslim edilmiştir. Ayrıntılı doğrulama durumu [doğrulama raporunda](reports/verification.md) bulunur. Sağlıklı bir Python ortamında ML komutu ölçülen sonuçları `reports/` altında üretir. Reliability/F1 ilişkisi gözlenen ilişki olarak yorumlanmalı, nedensellik kanıtı sayılmamalıdır.

## Sınırlamalar

- Bileşen formülleri ve eşit ağırlıklar alan bilgisiyle kalibre edilmelidir.
- Varsayılan geçerlilik aralıkları yalnızca üretilen şemaya yöneliktir.
- Bağlam analizleri keşifseldir ve gruplar örtüşebilir.
- Sensör tutarlılık analizi ekipman arızası teşhisi koymaz.
- Kontrollü deney tek bir sentetik süreç ve iki model ailesi kullanır.
- SQL dosyalarının doğrulanması harici bir SQL Server ve ODBC kurulumu gerektirir.
- Genel CSV parmak izi desteği, sabit şemalı ML deneyinden daha geniştir.

## Gelecek Geliştirmeler

- Geçerlilik kurallarını yönetilen metadata üzerinden tanımlama
- Skor ve performans değişimleri için bootstrap belirsizlik analizi
- Drift yöntemleri ve zaman serisi çapraz doğrulama karşılaştırmaları
- Veri seti sürüm hash'leri ve çalışma yapılandırma tabloları
- Ağırlıkları alan uzmanları ve gerçek operasyon sonuçlarıyla kalibre etme

---

# English

## Project Overview

Data Reliability Fingerprint is a Python, Microsoft SQL Server, and Streamlit project for examining where a dataset becomes less trustworthy. Instead of reporting only global missing-value and duplicate counts, it compares explainable reliability components across operational contexts and time, then measures how controlled degradation affects classification models.

## Research Question

> Is a dataset equally reliable under every condition? Where, when, and under which operating contexts does reliability decline, and how is machine-learning performance associated with that decline?

The project treats the answer as empirical and context-dependent. Its aggregate score is an application heuristic, not a universal or scientifically certified quality measure.

## Motivation

A global 3% missing rate can hide a 20% problem on one machine during one shift. A model can also respond differently to missingness, noise, and context-specific corruption even when their global quality scores look similar. This repository keeps component scores, context tables, temporal trends, model metrics, and assumptions visible so that the aggregate does not obscure the evidence.

## Features

- Six-component reliability fingerprint with explicit `Not Available` behavior
- Context analysis for user-selected categorical columns, with sample-size flags, completeness intervals, and multiplicity metadata
- Adaptive daily, weekly, or monthly temporal analysis
- Range validation, duplicate detection, robust outliers, correlations, rolling statistics, and regression-residual consistency checks
- Reproducible industrial sensor generator with context-specific and temporal defects
- Logistic Regression and Random Forest experiments under controlled missingness, noise, and night-shift corruption
- Time-ordered train/test split and train-only preprocessing through scikit-learn pipelines
- Streamlit upload workflow and six analysis pages
- SQL Server history, metrics, context, temporal, issue, and model tables
- T-SQL views, stored procedures, CTEs, subqueries, grouping, `CASE`, `LAG`, `ROW_NUMBER`, joins, and indexes
- Tests for numerical outcomes, unavailable metrics, edge cases, and leakage prevention

## Technology Stack

Python 3.11+; pandas, NumPy, SciPy, scikit-learn, Matplotlib, Seaborn, Plotly, Streamlit, pyodbc, python-dotenv, pytest; Microsoft SQL Server and T-SQL.

## Dataset

`data/generate_dataset.py` creates 36,000 clean base observations and an observed file containing appended duplicates. Load, speed, vibration, temperature, and pressure are correlated without being deterministic; machines and operating states have different distributions. Controlled missing values, invalid humidity, vibration spikes, M04 pressure inconsistency, a late temperature drift, and night/M09 missingness are injected.

The observed CSV contains no error labels. `synthetic_error_reference.csv` is evaluation-only, excluded from Git by default, and never used by the analyzer or models. See [synthetic error mechanisms](docs/synthetic_error_mechanisms.md).

For a real-data pathway, [UCI MetroPT-3](https://archive.ics.uci.edu/dataset/791/metropt%2B3%2Bdataset) is documented in [the real dataset guide](docs/real_dataset_guide.md). UCI describes it as operational metro-compressor data under CC BY 4.0. It is not bundled and no result is claimed for it.

## Reliability Fingerprint Methodology

All scores use 0–100. If prerequisites are absent, a component is `None`; it is not silently replaced by 100.

| Component | Definition and applicability | Main limitation |
|---|---|---|
| Completeness | `100 × (1 − missing cells / cells)` | Equal cell importance |
| Validity | `100 × (1 − invalid / observed checked)` over configured ranges | Rules are domain assumptions |
| Consistency | Penalty from robust sensor outliers, regression residuals, and very weak relationships | Anomaly is not fault diagnosis |
| Uniqueness | `100 × (1 − duplicate rows / rows)` using keys when supplied | Key selection changes meaning |
| Context Stability | `max(0, 100 − 3 × weighted SD of eligible group reliability)` | Overlapping groups and multiple comparisons |
| Temporal Stability | `max(0, 100 − 2.5 × period SD − positive deterioration)` | Aggregation can hide short incidents |

The default overall score is the equal-weight mean of available components. Available weights are renormalized, and the result retains which metrics participated. Full formulas and assumptions are in [methodology.md](docs/methodology.md).

## Context-Aware Analysis

Each selected context is grouped independently. A group's working score averages applicable completeness, validity, and uniqueness results. Groups under 30 rows are marked insufficient and excluded from context stability. The output includes a confidence interval for completeness and a Bonferroni-adjusted exploratory alpha; it deliberately avoids presenting every observed difference as statistically conclusive.

## Temporal Analysis

The analyzer selects daily bins for spans up to one week, weekly bins up to 120 days, and monthly bins beyond that. It reports completeness, validity, and their available-component mean. Invalid or absent timestamps make temporal stability unavailable without blocking the rest of the fingerprint.

## Machine Learning Experiments

The experiment sorts by timestamp, trains on the first 75%, and tests on the later 25%. Numeric median imputation and scaling plus categorical mode imputation and one-hot encoding are fit inside the training pipeline. Both classifiers are tested on:

1. observed baseline;
2. 10% missing numeric cells;
3. medium Gaussian numeric noise;
4. context-specific corruption of night-shift vibration and pressure.

Recorded results include accuracy, macro precision, macro recall, macro F1, confusion matrix, seed, row counts, and scenario reliability. Injection flags and identifiers are never features.

## Database Architecture

The normalized schema relates `datasets` to repeatable `analysis_runs`, then stores component metrics, context results, detected issues, temporal metrics, and model experiments by run. Foreign keys, checks, unique constraints, and query-oriented indexes are included. See [database design](docs/database_design.md).

## Installation

```powershell
git clone <your-repository-url>
cd data-reliability-fingerprint
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

On Windows, install Microsoft ODBC Driver 18 for SQL Server separately if persistence is required. Python-only analysis works without a running SQL Server.

## Configuration

```powershell
Copy-Item .env.example .env
```

The default uses Windows Authentication. For SQL Server Authentication, set both `DB_USERNAME` and `DB_PASSWORD`. Do not commit `.env`.

## Usage

Generate reproducible data:

```powershell
python data/generate_dataset.py
```

Run the complete CSV analysis and ML experiments:

```powershell
python -m src.main data/sample_data.csv --name industrial_sensor_data --ml
```

Outputs are written to `reports/fingerprint.json`, `context_results.csv`, `temporal_results.csv`, `detected_issues.csv`, and—when ML is enabled—`ml_experiments.csv`.

Run tests and syntax/import checks:

```powershell
python -m compileall src dashboard data tests
python -m pytest -q
```

## Dashboard

```powershell
python -m streamlit run dashboard/app.py
```

The pages are Overview, Data Profiling, Context Analysis, Temporal Analysis, ML Experiments, and Analysis History. CSV users choose context and timestamp columns. History displays a clear connection message and never represents unsaved results as persisted.

## Microsoft SQL Server setup

Run these files in SQL Server Management Studio in order:

1. `database/create_database.sql`
2. `database/create_tables.sql`
3. `database/views.sql`
4. `database/stored_procedures.sql`
5. `database/analytics_queries.sql` when you want example reports

Then copy `.env.example` to `.env`, adjust the server and driver, and verify the Analysis History page. Python uses parameterized `?` placeholders for values.

## Experimental Results

The generated 36,216-row dataset was analyzed successfully. The measured overall fingerprint was **99.6635**; component results are recorded in `reports/fingerprint.json`. A high aggregate does not imply that local context problems are absent.

This host's Windows Application Control policy blocked scikit-learn native DLLs, so numerical ML results were not fabricated. The experiment implementation and tests are included; the exact verification status is recorded in [the verification report](reports/verification.md). On a healthy Python environment, the ML command writes measured scenario results under `reports/`. Interpret the reliability/F1 relationship as association rather than causality.

## Limitations

- Component formulas and equal weighting require domain calibration.
- Default validity ranges apply to the generated schema, not arbitrary uploads.
- Context analyses are exploratory and groups can overlap.
- The sensor-consistency module does not diagnose equipment failure.
- The included controlled study uses one generated process and two model families.
- SQL scripts require an external SQL Server and ODBC installation; lack of a server does not imply successful database validation.
- Generic CSV fingerprinting is broader than the fixed-schema ML experiment.

## Future Improvements

- Learn validity constraints from governed metadata rather than source code.
- Add bootstrap uncertainty for score and performance changes.
- Compare drift detectors and time-series cross-validation.
- Add dataset-version hashes and run configuration tables.
- Validate scoring weights with domain experts and downstream incident outcomes.
