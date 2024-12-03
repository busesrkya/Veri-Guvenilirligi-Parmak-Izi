# Metodoloji

## Kapsam

Fingerprint, aynı yapılandırma altında karşılaştırma yapmak için tasarlanmış açıklanabilir bir uygulama skorudur; bilimsel olarak evrensel bir veri güvenilirliği ölçüsü değildir. Her bileşen 0–100 aralığındadır. Hesaplanamayan bileşenler `None` kalır ve 100 olarak doldurulmaz.

## Bileşenler

**Completeness** = `100 × (1 − eksik hücre / toplam hücre)`. Hücresi olmayan veri seti skorlanmaz.

**Validity** = `100 × (1 − geçersiz / gözlenen ve kontrol edilen)`. Yalnızca tanımlı aralık kuralına sahip kolonlardaki eksik olmayan değerler kontrol edilir. Eksiklik completeness bileşenine aittir. Sayıya çevrilemeyen ve aralık dışı değerler geçersizdir. Uygulanabilir gözlem yoksa metrik hesaplanamaz.

**Uniqueness** = `100 × (1 − tekrarlanan kayıt / kayıt)`. Anahtar kolon verilirse tekrar o anahtara göre, verilmezse bütün kolonlara göre hesaplanır. Boş veri seti skorlanmaz.

**Consistency**, kullanılabilen sensör kolonlarındaki dayanıklı marjinal aykırı değerleri ve regresyon residual anomalilerini birleştirir. Median absolute deviation aşırı sapmaları belirler. Titreşimin yük, sıcaklık ve basınçla doğrusal regresyonu büyük dayanıklı residual'ları bulur; hareketli istatistikler ayrıca raporlanır. Skor cezası `70 × dayanıklı aykırı oranı + 50 × residual anomali oranı` ve çok zayıf ilişki için küçük bir cezadır. Bu sonuç bir tutarsızlık işaretidir, ekipman arızası teşhisi değildir.

**Context Stability**, seçilen her grupta completeness, validity ve uniqueness bileşenlerini değerlendirir. Formül `max(0, 100 − 3 × uygun grup skorlarının ağırlıklı standart sapması)` biçimindedir. 30'dan az kaydı olan gruplar işaretlenir ve bileşen hesabından çıkarılır. Tablo, keşif amaçlı takip için Bonferroni düzeltilmiş alfa ve completeness güven aralığı sağlar; her farkı anlamlı ilan etmez.

**Temporal Stability**, geçerli zaman damgalarını veri aralığına göre günlük, haftalık veya aylık gruplar. Dönem güvenilirliği, kullanılabilen completeness ve validity değerlerinin ortalamasıdır. Formül `max(0, 100 − 2,5 × dönem standart sapması − pozitif başlangıç/bitiş kötüleşmesi)` biçimindedir. En az iki dönem gerekir.

## Genel skor

Genel skor, hesaplanabilen bileşenlerin ağırlıklı aritmetik ortalamasıdır. Varsayılan ağırlıklar eşittir ve proje varsayımıdır. Ağırlıklar yalnızca kullanılabilen metrikler üzerinde yeniden normalize edilir. Sonuç; `used_metrics`, `unavailable_metrics` ve normalize ağırlıkları saklar.

## Makine öğrenmesi deney tasarımı

Kayıtlar zamana göre sıralanır ve %75/%25 ayrılır; sonraki gözlemler test setidir. Sayısal medyan doldurma/ölçekleme ile kategorik mod doldurma/one-hot encoding işlemleri scikit-learn `Pipeline` içinde yalnızca eğitim verisine fit edilir. Logistic Regression ve Random Forest; gözlenen temel veri, %10 eksik sayısal hücre, orta sensör gürültüsü ve gece vardiyasına özgü eksiklik altında değerlendirilir. Accuracy, macro precision, macro recall, macro F1, confusion matrix, seed ve senaryo fingerprint değeri kaydedilir.

Deneyler kontrollü bozulma altında ilişki ölçer. Güvenilirlik skoru değişiminin performans değişimine neden olduğunu kanıtlamaz ve bozulmanın tekdüze olması beklenmez.

## Sınırlamalar

- Varsayılan aralıklar sentetik veri için alan varsayımıdır.
- Bağlam grupları örtüşebilir; grup skorları bağımsız değildir.
- Basit kararlılık formülleri açıklanabilirdir fakat üretim kullanımı için kalibrasyon ister.
- Zamansal toplulaştırma kısa süreli olayları gizleyebilir.
- Sentetik hatalar bütün gerçek veri toplama süreçlerini kapsamaz.
- Macro metrikler iki sınıfa eşit ağırlık verir fakat uygulamaya özgü hata maliyetinin yerini tutmaz.

