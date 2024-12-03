# Veritabanı tasarımı

`datasets` bir veri varlığını tanımlar; `analysis_runs` aynı veri seti üzerinde tekrarlanan analizleri saklar. Metrikler, bağlamlar, tespit edilen sorunlar, zamansal değerler ve model deneyleri bir analiz çalışmasına bağlıdır ve çalışma silindiğinde onunla birlikte silinir. Ana veri seti kaydı korunur. Check constraint'ler skor aralıklarını ve durum değerlerini, unique constraint'ler ise aynı çalışma içinde yinelenen metrik ve zamansal ölçümleri denetler.

Metrik ayrıntıları ve confusion matrix biçimleri değişebildiği için JSON metni olarak tutulur. Sık kullanılan ilişkiler nonclustered indexlerle desteklenir. UTC `DATETIME2(3)` değerleri sunucu saat dilimi belirsizliğini önler.

## Script sırası

1. `create_database.sql`: `master` bağlantısıyla veya veritabanı oluşturma yetkili hesapla çalıştırılır.
2. `create_tables.sql`
3. `views.sql`
4. `stored_procedures.sql`
5. Yalnızca örnek raporlar gerektiğinde `analytics_queries.sql`

Python repository katmanı `pyodbc` üzerinden `?` parametreleri kullanır; değerler SQL metnine birleştirilmez. Nesne adları uygulama içinde sabittir.

