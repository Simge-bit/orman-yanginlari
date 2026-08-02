# Kaynaklar ve Erişim Notları

Tüm dosyalar 2026-07-31 tarihinde indirilmiştir. Bu dosya her kaynağın
sağlığı, kapsamı ve bilinen sorunlarını belgeler — Faz 2 (temizlik) burada
başlar.

## Birincil kaynaklar

### `ogm_yillik_yangin_1988_2025.xls`
- **Kaynak:** T.C. Tarım ve Orman Bakanlığı, Orman Genel Müdürlüğü (OGM),
  "Ormancılık İstatistikleri 2025", Tablo 2.11 "Orman yangınları, 1988-2025"
- **URL:** https://www.ogm.gov.tr/tr/e-kutuphane-sitesi/Ormancilikistatistikleri/2.11%20Orman%20yang%C4%B1nlar%C4%B1%2C%201988-2025.xls
  — erişim: 2026-08-02. OGM Haziran 2026'da yıllığı yeni bir SharePoint
  listesine (`Ormancilikistatistikleri`) taşımış; her tablo artık ayrı bir
  öğe/dosya (eski tek-zip yapısının yerine), ve genel liste sayfası
  (`/tr/e-kutuphane/kitaplik/Ormancilik-istatistikleri`) dosyaları JS ile
  grupluyor, doğrudan linkleri göstermiyor — gerçek dosya adı `listfeed.aspx`
  (SharePoint RSS) üzerinden bulundu.
- **İçerik:** Yıl, yanan alan (ha), yangın sayısı, ve 1997'den itibaren neden
  kategorisine göre (Kasıt / İhmal-Kaza / Doğal / Sebebi Bilinmeyen) sayı ve
  alan kırılımı. 2025 satırı: 3.224 yangın, 81.473 ha.
- **En yetkili kaynak bu dosyadır** — diğer ikincil kaynaklarla (haber,
  blog) çelişki olursa buna güvenilir. Eski `ogm_yillik_yangin_1988_2024.xls`
  hâlâ `data/raw/`'da duruyor (provenance için), ama pipeline artık bu
  dosyayı okuyor.
- **Bilinen sorun:** 2024 için bu dosya 3.797 yangın / 27.485 ha veriyor;
  bazı ikincil kaynaklar (Greenpeace blog, çevresel göstergeler metni)
  3.408 / 26.101 rakamını veriyor. EFFIS'in bağımsız 2024 verisi (aşağıya
  bkz.) 27.485 ha ile bu dosyayı doğruluyor — bu yüzden 27.485 ha / 3.797
  yangın esas alınmalı, diğer rakam muhtemelen ön/geçici veri.

### `ogm_faaliyet_raporu_2025_yangin.csv` + `ogm_faaliyet_raporu_2025.pdf` — artık kullanılmıyor (superseded)
- Bu dosya, "Ormancılık İstatistikleri 2025" yıllığı henüz yayınlanmadığı
  dönemde (2026-07-31'e kadar) ulusal yıllık seriye 2025 eklemek için
  geçici bir kaynak olarak kullanılıyordu. 2026-08-02'de gerçek yıllık
  (Tablo 2.11, yukarı bkz.) bulunduğu için `01_ingest.py` artık bu dosyayı
  okumuyor — dosya sadece provenance için `data/raw/`'da duruyor.
- **Not:** İki kaynağın rakamları neredeyse özdeş ama birebir aynı değil
  (ör. ihmal-kaza sayısı: Faaliyet Raporu 1.774, yıllık Tablo 2.11 1.753;
  toplam alan ve toplam yangın sayısı her ikisinde de birebir aynı:
  81.473 ha / 3.224 yangın) — beklenen bir ön-rapor/kesin-rapor farkı,
  şimdi kesin (yıllık) rakam esas alınıyor.
- **Hâlâ geçerli olan kısıt:** Bu Faaliyet Raporu il (81 il) bazında kırılım
  vermiyor, sadece "Ek 6"da Orman Bölge Müdürlüğü (~30 bölge) bazında
  yangın sayısı VE alanı var (bkz. `ogm_faaliyet_raporu_2025_bolge_yangin.csv`
  altında) — bu iki dosya hâlâ kullanımda, sadece bölge kırılımı için.
  `cografi.json` / harita 2024'te kalmaya devam ediyor: "Ormancılık
  İstatistikleri 2025" listesinde il-bazlı Tablo 2.14 (`İllere göre orman
  yangınlarının dağılımı, 2025`) VE Tablo 2.12/2.13/2.15/2.16/2.17/2.18/
  1.3/1.6'nın 2025 sürümleri de listelendiği doğrulandı (OGM'nin
  `Ormancilikistatistikleri` SharePoint listesinin RSS akışında görülüyor),
  ANCAK bu dosyaların gerçek indirme adları görüntülenen başlıklarıyla
  eşleşmiyor ve gerçek adı ortaya çıkaracak her yöntem (anonim REST API,
  WebDAV PROPFIND, arama API'si, grup-genişletme AJAX'i, başlık varyasyonu
  denemesi) engellendi/başarısız oldu — sadece Tablo 2.11 (yukarıdaki
  yıllık dosya) rastlantısal olarak dosya adı=başlık olduğu için erişilebildi.
  İl/bölge/neden/orman-türü/silvikültür kırılımları bu yüzden 2024'te
  kalıyor; kullanıcı kendi tarayıcısından o SharePoint listesini açıp ilgili
  dosyaların gerçek linklerini bulabilirse ileride güncellenebilir.

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
- **İçerik:** Bölge müdürlüğü verisinin başlangıçta sadece 2025'te (tek
  yıl) olduğu düşünülüyordu — bu iki tablo aslında 21 yıllık (2004-2024)
  bir seri, her bölgenin kendi zaman içindeki eğilimini hesaplamayı
  mümkün kılıyor (bkz. cografi.json bolge_egim_2004_2024). Geniş
  (yıl=sütun) formatta geliyor, pipeline'da uzun (bölge, yıl, değer)
  formata çevriliyor (01_ingest.py).
- **Doğrulama:** Her yıl için 31 bölgenin (DKMPGM dahil) toplamı, tablonun
  kendi "Toplam-Total" satırıyla ve örtüşen yıllarda (2004-2024) ulusal
  `yillik_seri.csv` ile karşılaştırıldı — hiçbir yılda 2 ha'yı aşan bir
  fark yok (02_clean.py'de programatik kontrol).
- **Dikkat:** "Bölge Müdürlüğü" idari birimi il (81 il) ile birebir örtüşmez
  — bazı bölge müdürlükleri birden fazla ili kapsar. İl bazlı harita için
  `ogm_il_yangin_dagilimi_2024.xlsx` kullanılmalı, bu dosyalar zaman
  serisi/bölge kesitleri için tamamlayıcıdır.

### `ogm_vasif_dagilimi_2025.xlsx` (2024 sürümü de `ogm_vasif_dagilimi_2024.xlsx` olarak duruyor)
- **Kaynak:** OGM, Tablo 2.17 — yangınların orman vasfına göre dağılımı, 2025.
- **İçerik:** Yanan alanın orman türüne göre dağılımı: Normal Koru
  (sağlıklı/verimli), Boşluklu Kapalı Koru (bozuk), Normal/Boşluklu Kapalı
  Baltalık, Makilik, Ağaçlandırma Sahası. Bölge müdürlüğü bazında (DKMPGM
  dahil, 31 satır) + "Toplam-Total".
- **Doğrulama (2024):** Bileşenlerin toplamı satır bazında beyan edilen
  toplam alanla, "Toplam-Total" satırı ise 2024 ulusal yangın toplamıyla
  (~0,4 ha farkla) eşleşiyor.
- **Bilinen sorun (2025 — yeni):** 2024'ün aksine, 2025 tablosunda bileşen
  toplamı beyan edilen alanla artık eşleşmiyor. Ulusal "Toplam-Total"
  satırında bileşenler toplamı (92.508 ha) beyan edilen toplam alandan
  (81.473 ha) %13,5 daha fazla. Bölge bazında fark çok daha değişken ve
  bazı bölgelerde çok daha büyük (bir bölgede bileşenler beyan edilen
  alanın ~4,3 katına çıkıyor, bazılarında ise hafifçe eksik kalıyor) —
  bu, kategorilerin bu yıl artık birbirini dışlamadığını (bir yangının
  alanının birden fazla vasıf kategorisinde sayıldığını) düşündürüyor.
  OGM'nin kendi tablosunda var, düzeltilmedi, footnote'larda bir açıklama
  da yok. Sitede sadece ULUSAL toplam kullanıldığı için (bölge bazında bir
  vasıf grafiği yok), gösterilen rakam sadece %13,5'lik farkı taşıyor —
  ama bu satırın altındaki veri kalitesinin bu yıl daha zayıf olduğu
  açıkça belgelenmeli.

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

### `ogm_neden_bolge_alansal_2024.xlsx` / `ogm_neden_bolge_sayisal_2024.xlsx`
- **Kaynak:** OGM, Tablo 2.15 (alan) / 2.16 (sayı) — yangınların çıkış
  sebeplerine göre bölge müdürlüklerine dağılımı, 2024.
- **İçerik:** Ulusal 4 kategorinin (kasıt/ihmal-kaza/doğal/bilinmeyen)
  çok daha ince kırılımı, bölge müdürlüğü bazında: İhmal (anız, çöplük,
  avcılık/çoban ateşi, sigara, piknik, diğer), Kasıt (terör, kundaklama,
  açma/arazi genişletme, diğer), Kaza (enerji hattı, trafik, diğer),
  Bilinmeyen, Doğal (yıldırım). "Toplam-Total" satırı ulusal toplamı
  veriyor.
- **Doğrulama:** Her satırda 14 alt-kategorinin toplamı, tablonun kendi
  "Toplam" sütunuyla eşleşiyor (02_clean.py'de kontrol ediliyor) — tek
  istisna "DKMPGM" (Milli Parklar) satırı, ~2,9 ha'lık küçük bir OGM
  kaynaklı tutarsızlıkla (bileşenler 1.286,4 ha, beyan edilen toplam
  1.289,4 ha). Bu iki tablonun "Toplam-Total" satırı, aynı yılın ulusal
  4-kategori tablosuyla (Tablo 2.11) birebir eşleşmiyor — OGM'nin aynı
  yıllığındaki farklı tablolar arasında birkaç yüzdelik bilinen bir
  tutarsızlık var (örn. kasıt toplamı bu tabloda 218,4 ha, ulusal
  tabloda 223 ha). Yangın sayısı toplamı (3.797) ise ulusal tabloyla
  birebir eşleşiyor.
- **Bu tablo, silvikültür tablosundan (2.18) farklı olarak "DKMPGM"
  (Doğa Koruma ve Milli Parklar Genel Müdürlüğü) satırını içeriyor** —
  yani 30 bölge müdürlüğü + DKMPGM = 31 satır (silvikültür tablosunda
  DKMPGM hiç yok, 30 satır).
- **Bilinen sınırlama:** 2025 için bu düzeyde bir kırılım hiçbir resmi
  kaynakta yok (2025 Faaliyet Raporu sadece kaba 5 kategori veriyor) —
  bu yüzden 2024'te kalıyor.

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

## OGM'nin yayın takvimi — veri gecikmesi

OGM'nin duyurular arşivinde ("...Ormancılık İstatistikleri **YIL** Yayınlandı"
kalıbıyla, `https://www.ogm.gov.tr/tr/duyurular/resmi-istatistik-programi-
kapsaminda-yer-alan-ormancilik-istatistikleri-<YIL>-yayinlandi`) bulunan 3
duyurunun yayın tarihleri:

| Veri yılı | Yayın tarihi | Yıl sonundan gecikme |
|---|---|---|
| 2023 | 26.06.2024 | 178 gün (~5,8 ay) |
| 2024 | 26.06.2025 | 177 gün (~5,8 ay) |
| 2025 | 26.06.2026 | 177 gün (~5,8 ay) |

Üç yılda da neredeyse aynı gün (26 Haziran) — sabit bir kurumsal takvim,
tesadüf değil. Bu kalıba göre **2026 verisi ancak Haziran 2027'de
yayınlanır**; bu proje o tarihe kadar en güncel resmi veri olarak 2025'te
kalacak (bkz. `metodoloji.json` bilinen sınırlamalar). Bu 3 duyuru dışında
(2018-2022 için) aynı URL kalıbıyla bir duyuru bulunamadı (404) — daha eski
yıllar için OGM ya farklı bir duyuru başlığı/URL kalıbı kullanmış ya da
duyuru arşivi bu kadar geriye gitmiyor, bu yüzden 3 yıldan daha uzun bir
tarihsel seri kurulamadı.

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
