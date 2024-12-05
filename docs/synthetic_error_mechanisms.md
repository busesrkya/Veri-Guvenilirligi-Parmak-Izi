# Sentetik hata mekanizmaları

Veri üreticisi önce makine etkileri, çalışma durumları, günlük sıcaklık döngüsü ve birbiriyle ilişkili yük, hız, sıcaklık, basınç ve titreşim değerleri içeren temiz fakat deterministik olmayan bir endüstriyel süreç oluşturur. Ardından varsayılan olarak `43` seed değeriyle bu verinin bir kopyasına kontrollü sorunlar ekler.

| Mekanizma | Enjeksiyon kuralı | Amaç |
|---|---|---|
| Bağlama özgü eksiklik | M09 makinesinin gece vardiyası titreşim gözlemlerinin %34'ünü kaldırır | Genel ortalamanın gizlediği problemi göstermek |
| Rastgele eksiklik | Kayıtların %1,8'inde dört sayısal kolondan birini boş bırakır | Genel completeness testi |
| Sensör sıçraması | Titreşim değerlerinin %0,9'unu 4–9 arası katsayıyla çarpar | Dayanıklı aykırı değer tespiti |
| Geçersiz ölçüm | Nem değerlerinin %0,4'ünü -12 veya 135 yapar | Kural tabanlı validity testi |
| Dağılım kayması | Son %22'lik döneme kademeli 0–10 derece sıcaklık farkı ekler | Zamansal bozulma testi |
| Sensör tutarsızlığı | En fazla 300 adet M04 basınç değerini yüksek basınç dağılımıyla değiştirir | İlişki ve residual analizi |
| Tekrarlanan kayıt | Kayıtların %0,6'sını aynen sona ekler | Uniqueness testi |

`synthetic_error_reference.csv`, enjekte edilen kayıt kimliklerini yalnızca bağımsız değerlendirme için saklar. Analiz ve ML özellikleri bu dosyayı kullanmaz. Dosya varsayılan olarak Git dışında tutulur; gözlenen CSV içinde hata işareti bulunmaz.

