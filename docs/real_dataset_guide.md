# Gerçek veri seti doğrulama rehberi

## Önerilen kaynak

[UCI MetroPT-3](https://archive.ics.uci.edu/dataset/791/metropt%2B3%2Bdataset), bir metro treninin Air Production Unit kompresöründen alınmış gerçek zaman serisi sensör ölçümlerini içerir. UCI veri kartı 1.516.948 gözlem, 15 özellik ve Creative Commons Attribution 4.0 lisansı bildirir. Uyarlanmış veriyi yeniden dağıtırken veri setine atıf yapılmalı ve güncel lisans koşulları korunmalıdır.

Bu proje veri setini paketlemez ve veri üzerinde analiz yapılmış gibi sonuç sunmaz. CSV dosyasını UCI kaynağından indirin, güncel veri kartını ve lisansı inceleyin, ardından dashboard'a yükleyin.

## Önerilen kolon eşlemesi

- Kaynak zaman alanını `timestamp` olarak yeniden adlandırın veya dashboard'da zaman kolonu olarak seçin.
- `TP2`, `TP3`, `H1`, `DV_pressure` ve `Reservoirs` gibi basınç kanallarını sayısal sensör ölçümü olarak kullanın.
- `Oil_temperature` kolonunu sıcaklık, `Motor_current` kolonunu ek sayısal ölçüm olarak değerlendirin.
- `COMP`, `DV_eletric`, `Towers`, `MPG` ve `LPS` gibi ikili operasyon sinyallerini yeterli grup büyüklüğü bulunduğunda bağlam olarak seçin.
- Veri setine özgü geçerlilik aralıkları tanımlayın. Projedeki varsayılan aralıklar sentetik şemaya göre ayarlanmıştır ve MetroPT-3 birimlerine doğrudan uygulanmamalıdır.
- MetroPT-3, bu projenin `quality_label` şemasına sahip değildir. Genel fingerprint analizi etiketsiz çalışır; sınıflandırma deneyi için veri seti belgesine dayanan savunulabilir bir hedef uyarlaması gerekir.

Bellek kullanımını sınırlamak için önce zaman açısından kesintisiz bir alt küme kullanılabilir. Amaç zamansal kaymayı ölçmekse rastgele örnekleme yapılmamalıdır.

