# Doğrulama raporu

Doğrulama tarihi: 13 Ekim 2026

## Başarılı kontroller

- `python -m compileall -q src dashboard data tests`: bütün Python dosyalarının sözdizimi kontrol edildi, hata yok.
- Sentetik veri üreticisi varsayılan seed değerleriyle çalıştırıldı.
- `data/sample_data.csv`: 36.216 satır, 13 kolon.
- Enjekte edilen/ölçülen temel durumlar: 216 tekrarlanan `record_id`, 988 eksik hücre ve 144 aralık dışı nem değeri.
- ML dışındaki testler: **16 passed**.
- Fingerprint analizi gerçek üretilen veri üzerinde çalıştırıldı ve `reports/` çıktıları oluşturuldu.
- Hesaplanan bileşenler:
  - Completeness: 99,7901
  - Validity: 99,8451
  - Consistency: 99,3249
  - Uniqueness: 99,4036
  - Context Stability: 99,6754
  - Temporal Stability: 99,9422
  - Genel skor: 99,6635
- `detected_issues.csv` içinde 44 toplulaştırılmış sorun kaydı oluşturuldu.
- `requirements.txt` kurulumu tamamlandı ve `pip check` sonucu `No broken requirements found` oldu.
- SQL dosyalarında istenen JOIN, GROUP BY, HAVING, CASE, CTE, alt sorgu, LAG, ROW_NUMBER, view ve stored procedure yapılarının varlığı statik olarak kontrol edildi.

## Bu ortamda doğrulanamayanlar

- Windows Application Control, indirilen scikit-learn native DLL dosyalarını engelledi. Bu nedenle iki ML testi ile Logistic Regression/Random Forest deneyleri bu bilgisayarda çalıştırılamadı. Kod ve testler projede mevcuttur; sayısal ML sonucu üretilmiş gibi gösterilmemiştir.
- Streamlit paketi ve dashboard bağımlılıkları import edildi; ancak aynı bozuk Python kurulumunda sunucu dinleme aşamasına geçmedi. Dashboard dosyasının sözdizimi kontrolü başarılıdır, canlı arayüz doğrulanmamıştır.
- `sqlcmd` yüklüdür fakat `localhost` üzerinde erişilebilir SQL Server instance'ı bulunamadı. SQL scriptleri statik olarak kontrol edildi; veritabanı oluşturma, persistence ve sorgu sonuçları çalıştırılmış gibi sunulmamıştır.
- Sistem Python'u çalışırken kurulum yolunu çözemediğine dair uyarı veriyor ve bu cihazda `.venv` oluşturma işlemi `ensurepip` aşamasında başarısız oldu. Normal ve sağlıklı bir Python 3.11+ kurulumunda README'deki standart venv adımları kullanılmalıdır.
