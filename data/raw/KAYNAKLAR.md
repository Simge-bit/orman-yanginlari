# Kaynaklar ve Erişim Notları

Tüm dosyalar 2026-07-31 tarihinde indirilmiştir. Bu dosya her kaynağın
sağlığı, kapsamı ve bilinen sorunlarını belgeler — Faz 2 (temizlik) burada
başlar.

## Birincil kaynaklar

### `ogm_yillik_yangin_1988_2024.xls`
- **Kaynak:** T.C. Tarım ve Orman Bakanlığı, Orman Genel Müdürlüğü (OGM),
  "Ormancılık İstatistikleri 2024", Tablo 2.11 "Orman yangınları, 1988-2024"
- **URL:** https://www.ogm.gov.tr/tr/e-kutuphane-sitesi/Istatistikler/Ormancılık%20İstatistikleri/Ormancılık%20İstatistikleri%202024.zip
  (bkz. `ogm_ormancilik_istatistikleri_2024_kaynak.zip` — orijinal zip, tam
  provenance için saklanıyor)
- **İçerik:** Yıl, yanan alan (ha), yangın sayısı, ve 1997'den itibaren neden
  kategorisine göre (Kasıt / İhmal-Kaza / Doğal / Sebebi Bilinmeyen) sayı ve
  alan kırılımı.
- **En yetkili kaynak bu dosyadır** — diğer ikincil kaynaklarla (haber,
  blog) çelişki olursa buna güvenilir.
- **Bilinen sorun:** 2024 için bu dosya 3.797 yangın / 27.485 ha veriyor;
  bazı ikincil kaynaklar (Greenpeace blog, çevresel göstergeler metni)
  3.408 / 26.101 rakamını veriyor. EFFIS'in bağımsız 2024 verisi (aşağıya
  bkz.) 27.485 ha ile bu dosyayı doğruluyor — bu yüzden 27.485 ha / 3.797
  yangın esas alınmalı, diğer rakam muhtemelen ön/geçici veri.

### `ogm_faaliyet_raporu_2025_yangin.csv` + `ogm_faaliyet_raporu_2025.pdf`
- **Kaynak:** T.C. Tarım ve Orman Bakanlığı, OGM, "2025 Yılı Faaliyet
  Raporu", Tablo 16 (çıkış sebebine göre sayısal dağılım, 2021-2025) ve
  Tablo 17 (alansal dağılım, 2021-2025).
- **URL:** https://www.ogm.gov.tr/tr/e-kutuphane-sitesi/FaaliyetRaporu/2025%20-%20Orman%20Genel%20M%C3%BCd%C3%BCrl%C3%BC%C4%9F%C3%BC%20Faaliyet%20Raporu.pdf
- **Neden bu kaynak:** Erişim tarihinde (2026-07-31) OGM'nin "Ormancılık
  İstatistikleri" yıllığının 2025 sürümü henüz yayınlanmamıştı (portal hâlâ
  2024.zip'te duruyor) ve OGM'nin Haziran 2026 haber bülteni de yangın
  konusunu içermiyordu (ağaçlandırma/sertifika konularıydı). Faaliyet
  Raporu, 2025 yangın rakamlarını içeren tek resmi OGM yayını olarak
  bulundu.
- **İçerik:** 2025: 3.224 yangın, 81.473 ha; kasıt/ihmal-kaza/doğal/
  bilinmeyen kırılımı (sayı+alan). `ogm_faaliyet_raporu_2025_yangin.csv`
  içinde sadece 2025 satırı tutuluyor (2021-2024 zaten
  `ogm_yillik_yangin_1988_2024.xls`'te var).
- **Bilinen sorun:** Bu rapor 2021-2024 için de aynı tabloları veriyor,
  ama kategori dağılımı `ogm_yillik_yangin_1988_2024.xls`'teki değerlerden
  hafifçe farklı (ör. 2024 "Sebebi Belirlenemeyen": bu raporda 1.111,
  yıllıkta 1.084 — toplam her ikisinde de 3.797, sadece kategoriler arası
  dağılım farklı). Bu yüzden 2021-2024 için yine yıllık istatistik dosyası
  esas alınıyor, sadece 2025 bu rapordan ekleniyor — iki farklı OGM
  yayınının kategori sınırları arasında küçük bir tutarsızlık olduğu
  metodoloji sayfasında belirtiliyor.
- **Eksik:** Bu rapor il (81 il) bazında kırılım vermiyor, sadece "Ek 6"da
  Orman Bölge Müdürlüğü (~30 bölge) bazında yangın sayısı VE alanı var
  (bkz. `ogm_faaliyet_raporu_2025_bolge_yangin.csv` altında). Bu yüzden
  `cografi.json` / harita 2024'te kalmaya devam ediyor — 2025 il bazında
  veri hiçbir resmi kaynakta yok.

### `ogm_faaliyet_raporu_2025_bolge_yangin.csv` + `ogm_faaliyet_raporu_2025_bolge_neden.csv`
- **Kaynak:** Aynı "2025 Yılı Faaliyet Raporu", Ek 6 "Orman Yangın
  Sayılarının Orman Bölge Müdürlükleri Dağılımı, 2025" (basılı sayfa 61,
  PDF sayfa 73).
- **İçerik:** 30 bölge müdürlüğü + Milli Parklar için yangın sayısı ve
  yanan alan (`..._bolge_yangin.csv`), ve İhmal/Kasıt/Kaza/Sebebi
  Belirlenemeyen/Yıldırım kırılımı, sayı+alan (`..._bolge_neden.csv`).
  Ulusal 4 kategoriyle (İhmal-Kaza birleşik, Yıldırım=Doğal) tutarlı olsun
  diye pipeline'da (02_clean.py clean_bolge_neden_2025) yeniden gruplanıyor.
- **Doğrulama:** PDF çift sütunlu, karmaşık bir tablo olduğu için önce
  `pdftotext -layout` ile çıkarılıp PDF sayfasının kendisiyle (Read aracı,
  görsel) satır satır karşılaştırıldı; ardından her satırın 5 alt
  kategorisi kendi TOPLAM'ıyla ve `..._bolge_yangin.csv`'nin önceden
  doğrulanmış değerleriyle programatik olarak (scratchpad/
  bolge_neden_dogrula.py) çapraz kontrol edildi — 0 hata, tam eşleşme.
- **Bölge müdürlüğü il değildir:** Bazı bölgeler birden fazla ili kapsar;
  bu tablo il haritasının yerine değil yanına eklendi.

### `ogm_il_yangin_dagilimi_2024.xlsx`
- **Kaynak:** OGM, Ormancılık İstatistikleri 2024, Tablo 2.14 "İllere göre
  orman yangınlarının dağılımı, 2024"
- **İçerik:** 81 il için İBBS kodu, il adı, yangın sayısı, yanan alan (ha).
  Sadece 2024 yılı — çok yıllı il bazında seri bu yayında yok, geçmiş
  yıllar için ayrı yılların zip'leri indirilmeli (bkz. aşağıdaki not).

### `ogm_bolge_alansal_2004_2024.xlsx`, `ogm_bolge_sayisal_2004_2024.xlsx`
- **Kaynak:** OGM, Tablo 2.12 / 2.13 — Orman Bölge Müdürlüğü bazında
  2004-2024 alansal/sayısal dağılım.
- **Dikkat:** "Bölge Müdürlüğü" idari birimi il (81 il) ile birebir örtüşmez
  — bazı bölge müdürlükleri birden fazla ili kapsar. İl bazlı harita için
  `ogm_il_yangin_dagilimi_2024.xlsx` kullanılmalı, bu dosyalar zaman
  serisi/bölge kesitleri için tamamlayıcıdır.

### `ogm_neden_bolge_alansal_2024.xlsx`, `ogm_neden_bolge_sayisal_2024.xlsx`
- **Kaynak:** OGM, Tablo 2.15 / 2.16 — çıkış nedeni × bölge müdürlüğü, 2024.

### `ogm_vasif_dagilimi_2024.xlsx`
- **Kaynak:** OGM, Tablo 2.17 — yangınların orman vasfına göre dağılımı, 2024.

### `ogm_silvikultur_degerlendirme_2024.xlsx`
- **Kaynak:** OGM, Tablo 2.18 — yanan alanların silvikültürel değerlendirmesi, 2024.
- **İçerik:** 2024'te yanan alanın (Orman Bölge Müdürlüğü bazında, 30 bölge +
  "Toplam-Total" satırı) hangi işleme alındığı: zarar görmeyen (örtü
  yangını), doğal/suni gençleştirme, rehabilitasyon, ağaçlandırma programı,
  teknik işlem gerekmediği için korumaya alınan, ve "gelecek yıllara
  bırakılan" (henüz işleme alınmamış). Milli Parklar bu tabloda ayrı
  sınıflandırılmış, dahil değil (not olarak tabloda belirtiliyor).
- **Doğrulama:** "Toplam-Total" satırı (27.485 ha) hem 30 bölgenin kendi
  toplamıyla (27.485,17 ha) hem de 2024 ulusal yangın toplamıyla
  (`yillik_seri.csv`) birebir eşleşiyor — pipeline'da (02_clean.py) her iki
  yönde de programatik kontrol var.
- **Bilinen sorun:** Balıkesir satırında bileşenlerin toplamı (261,41 ha)
  ile beyan edilen toplam alan (260,86 ha) arasında ~0,55 ha'lık küçük bir
  yuvarlama farkı var (OGM'nin kendi tablosunda) — düzeltilmedi, olduğu
  gibi bırakıldı.
- **Yorum notu:** "Gelecek yıllara bırakılan" kategorisi, o alanın
  ağaçlandırılmayacağı ya da başka bir amaçla kullanılacağı anlamına
  gelmez — sadece rapor tarihi itibarıyla henüz somut bir işleme/karara
  bağlanmadığını gösterir. Bu tablo "yanan alan imara mı açıldı" sorusuna
  cevap vermez (OGM böyle bir istatistik yayınlamaz, zaten Anayasa m.169
  gereği yanan orman arazisinin amacı değiştirilemez) — sadece "aktif
  ağaçlandırma/gençleştirme işlemine alındı mı, yoksa bekliyor mu" sorusuna
  resmi bir cevap verir.

### `ref_orman_alani_il_2024.xlsx` / `ref_orman_alani_il_2024_alt.xlsx`
- **Kaynak:** OGM, Tablo 1.6 / 1.3 — orman alanı, serveti ve cari artımının
  il düzeyinde dağılımı, 2024. Yangın yoğunluk indeksi (yanan alan / toplam
  orman alanı) hesaplamak için referans.

### `effis_ulke_karsilastirma_1980_2024.xlsx`
- **Kaynak:** EFFIS / Copernicus Emergency Management Service, "Forest
  Fires in Europe, Middle East and North Africa" yıllık raporu, ülke
  karşılaştırma tablosu.
- **URL:** https://forest-fire.emergency.copernicus.eu/effis/applications/data-and-services/report_2024.xlsx
- **İçerik:** 1980-2024, iki sayfa (yanan alan ha, yangın sayısı), ~30 ülke
  dahil TUR, GRC, ESP, ITA, PRT, FRA (config.yaml'daki karşılaştırma
  ülkeleri burada mevcut).
- **Çapraz doğrulama:** 2024 Türkiye satırı (27.485 ha) OGM'nin kendi
  tablosuyla (`ogm_yillik_yangin_1988_2024.xls`) birebir eşleşiyor —
  yukarıdaki 2024 rakamı tartışmasını bu dosya çözüyor.

### `tr_iller.geojson`
- **Kaynak:** cihadturhan/tr-geojson (GitHub, OpenStreetMap türevi, ODbL
  lisans), `tr-cities-utf8.json` dosyası.
- **URL:** https://raw.githubusercontent.com/cihadturhan/tr-geojson/master/geo/tr-cities-utf8.json
- **İçerik:** 81 il sınırı, her feature'da sadece `name` property'si var.
- **Bilinen sorun (Faz 2'de çözülecek):** GeoJSON'da il adı "Afyon" olarak
  geçiyor, OGM tablolarında "Afyonkarahisar" — il eşleme tablosunda bu ve
  benzeri farklar (örn. bazı kaynaklarda "Şanlıurfa" vs "Sanliurfa" ascii
  yazımı) elle kontrol edilmeli.

## Canlı katman (istisna: bu bir "raw" dosyası değil)

`web/assets/data/hotspots.json`, diğer her şeyin aksine `data/raw/`'dan
gelmiyor — `src/fetch_hotspots.py` tarafından CI'da (hem push'ta hem
3 saatte bir cron ile) NASA FIRMS'in VIIRS_SNPP_NRT sıcak nokta API'sinden
canlı çekiliyor, `tr_iller.geojson` sınırıyla kırpılıyor. Kaynak:
https://firms.modaps.eosdis.nasa.gov/ , API key `FIRMS_MAP_KEY` GitHub
Actions secret'ı olarak saklanıyor (repo'da veya kodda hiçbir yerde açık
yazılı değil). FIRMS API'sinin CORS desteği olmadığı için tarayıcıdan
doğrudan çağrılamıyor — bu yüzden sunucu tarafında (CI) çekilip statik
JSON olarak gömülüyor. Cografi sayfasında 2024 choropleth'inden ayrı,
açıkça "canlı/son 3 gün" etiketiyle gösteriliyor — iki katman farklı
zaman dilimlerini temsil ediyor, karıştırılmamalı.

Pencere kasıtlı olarak 1 gün değil 3 gün (FIRMS azami 5 gün destekliyor):
tek günlük pencerede hâlâ süren bir yangın, uydunun o gün üzerinden tam
geçmemesi gibi teknik bir sebeple haritadan aniden kaybolabiliyordu — bu
kullanıcı geri bildirimiyle fark edildi (test: Antalya 1 günlük pencerede
0 gösteriyordu, 3 günlükte 35 konum çıktı). Ham tespitler ~1km'lik konum
hücrelerine kümeleniyor (aynı hücre içinde saatler/günler süren tekrar
tespitler tek "küme" olarak sayılıyor) — hem 3 günlük pencerede bine
çıkabilen ham nokta sayısını haritada okunabilir tutmak hem de "bu konum
kaç kez tekrar tespit edildi" (süreklilik sinyali) için. Her kümenin en
son kaç saat önce görüldüğü haritada renk/opaklıkla kodlanıyor (koyu=taze
≤12 saat, soluk=36+ saat) — ama bu yine "kesin hâlâ yanıyor" veya "kesin
söndü" demek DEĞİL, sadece "ısı ne zaman algılandı" bilgisinin görsel bir
özeti.

Her kümenin il adı kendi `tr_iller.geojson`'umuzdan (nokta-içinde-poligon,
her zaman güvenilir). İlçe/köy adı ise OpenStreetMap Nominatim'in ücretsiz
reverse-geocoding servisinden (https://nominatim.openstreetmap.org) —
bu, resmi bir istatistik kaynağı değil, sadece "bu koordinat nerede"
sorusuna cevap veren bir yer-adı servisi; VIIRS'in ~375m piksel
çözünürlüğü nedeniyle zaten yaklaşık bir konum, ilçe/köy adı da buna göre
"en yakın yerleşim" olarak okunmalı, kesin nokta olarak değil. Nominatim'in
kullanım politikasına uymak için konum kümesi başına tek sorgu yapılıyor
ve toplam sorgu sayısı 80 ile sınırlanıyor (bkz. src/fetch_hotspots.py
NOMINATIM_MAX_SORGU) — büyük bir yangın günü yüzlerce ham tespit gelse
bile servise aşırı yüklenilmiyor, sınırı aşan kümeler için sadece il adı
gösterilir.

## İkincil kaynaklar kullanılmıyor

Bilinçli karar: haber sitesi, blog ve dernek/STK derlemesi gibi ikincil
kaynaklar (daha önce `destek/` altında tutulan Ormancılar Derneği sayfası,
Çevresel Göstergeler sayfası, verikaynagi.com grafiği ve grafik görselleri)
projeden çıkarıldı. Bu proje sadece birincil/resmi istatistik yayınlarına
(OGM, EFFIS/Copernicus) dayanır. Yukarıdaki 2024 rakamı çelişkisi zaten
iki bağımsız resmi kaynağın (OGM tablosu + EFFIS raporu) birbirini
doğrulamasıyla çözüldü; ikincil kaynaklara ihtiyaç kalmadı.

## Eksikler / Faz 1 devamı için notlar

- **EFFIS/Copernicus 2025 raporu henüz yok** (erişim: 2026-07-31) — ülke
  karşılaştırması (`karsilastirma.json`) 2024'te kalıyor. EFFIS 2025
  raporu yayınlanınca `effis_ulke_karsilastirma_1980_2024.xlsx` yerine
  yeni sürüm indirilip pipeline yeniden çalıştırılmalı.
- **İl bazında 2025 verisi hiçbir resmi kaynakta yok** — ne yıllık
  istatistik (henüz yayınlanmadı) ne de Faaliyet Raporu (sadece bölge
  müdürlüğü bazında, alan olmadan) bunu veriyor. `cografi.json` 2024'te
  kalmaya devam ediyor.
- **Çok yıllı il bazında seri yok:** `ogm_il_yangin_dagilimi_2024.xlsx`
  sadece 2024'ü kapsıyor. Geçmiş yıllar için il kırılımı istenirse, aynı
  "Ormancılık İstatistikleri" zip'lerinin 2020-2023 sürümleri de
  `https://www.ogm.gov.tr/tr/e-kutuphane-sitesi/Istatistikler/Ormancılık%20İstatistikleri/Ormancılık%20İstatistikleri%20<YIL>.zip`
  kalıbıyla indirilip aynı Tablo 2.14 çıkarılabilir (2020 için `.rar`
  uzantılı, diğerleri `.zip`).
- **İklim verisi henüz eklenmedi** (yol haritasında opsiyonel olarak
  belirtilmişti) — MGM (Meteoroloji Genel Müdürlüğü) sıcaklık/kuraklık
  istatistikleri sonraki bir adımda eklenebilir.
- **Zip dosya adlarındaki Türkçe karakterler eski bir DOS/Windows kod
  sayfasıyla (cp437/cp857 karışımı) kodlanmış** — macOS'un `unzip` komutu
  bunları UTF-8 locale'de açamıyor ("Illegal byte sequence" hatası).
  Orijinal zip (`ogm_ormancilik_istatistikleri_2024_kaynak.zip`) yine de
  saklandı; içindeki dosyalara Python `zipfile` + `cp437`/`cp857` decode ile
  erişilebilir (bu oturumda kullanılan yöntem).
