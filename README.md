# Türkiye Orman Yangınları — Veri Analizi ve Site

Türkiye'deki orman yangınlarına dair kamuya açık verilerin (OGM, EFFIS, TÜİK)
temizlenip analiz edildiği ve sonuçların statik bir çok sayfalı web sitesinde
sunulduğu proje.

**Canlı site:** https://simge-bit.github.io/orman-yanginlari/

## Mimari

Üç katman, tek yönlü akış:

```
data/raw (kaynaklar) → src/ pipeline (ingest→clean→transform→analyze→export) → web/ (statik site)
```

Analiz ile sunum arasındaki tek bağ `data/processed/*.json` dosyalarıdır — bu,
JSON şeması sabit kaldığı sürece iki tarafın birbirinden bağımsız
değiştirilebileceği bir sözleşmedir.

- `data/raw/` — indirilen ham veri, dokunulmaz, git'te tutulur
- `data/interim/` — temizlenmiş ara çıktı, git'e girmez (üretilir)
- `data/processed/` — site için hazır JSON'lar, git'e girmez (üretilir)
- `src/` — analiz pipeline'ı (Python)
- `tests/` — veri doğrulama testleri (il eşleşmesi, oran toplamları vb.)
- `notebooks/` — keşifsel analiz, üretim koduna dahil değil
- `web/` — statik site (HTML/CSS/JS), `web/assets/data/` altında JSON'ları okur

## Kurulum

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Pipeline'ı çalıştırma

```bash
python src/01_ingest.py
python src/02_clean.py
python src/03_transform.py
python src/04_analyze.py
python src/05_export.py
```

Her adım bir öncekinin çıktısını okur, kendininkini yazar. Veri güncellenince
sadece `data/raw/` değiştirilir, pipeline baştan çalıştırılır, JSON'lar
otomatik yenilenir.

## Canlı sıcak nokta katmanı

`cografi.html` haritasında 2024 choropleth'in üzerinde, NASA FIRMS'ten
(VIIRS uydu verisi) çekilen canlı sıcak nokta katmanı da var. Bu,
01-05 pipeline'ının bir parçası değil — ayrı çalışan `src/fetch_hotspots.py`
tarafından besleniyor:

```bash
FIRMS_MAP_KEY=... python src/fetch_hotspots.py
```

Ücretsiz anahtar: https://firms.modaps.eosdis.nasa.gov/api/map_key/ .
CI'da bu anahtar `FIRMS_MAP_KEY` adında bir GitHub Actions secret'ı olarak
saklanır, koda veya repoya asla açık yazılmaz. FIRMS API'sinin CORS desteği
olmadığı için tarayıcıdan doğrudan çağrılamıyor — bu yüzden veri CI'da
(hem her push'ta hem 3 saatte bir cron ile) sunucu tarafında çekilip
`web/assets/data/hotspots.json` olarak statik gömülüyor.

## Testleri çalıştırma

```bash
pytest tests/
```

## Siteyi görüntüleme

`data/processed/*.json` dosyaları `web/assets/data/` içine kopyalandıktan
sonra `web/` klasörünü bir statik sunucuyla aç (ör. `python -m http.server`).

## Parametreler

Tüm yıl aralığı, eşik değerleri ve kaynak künyeleri `config.yaml` içinde.
Kodun içine sabit değer gömülmez.

## Sayfa–veri eşlemesi

| Sayfa | Veri kaynağı |
|---|---|
| `index.html` | `ozet.json` |
| `trend.html` | `trend.json` |
| `cografi.html` | `cografi.json` + `tr_iller.geojson` |
| `nedenler.html` | `nedenler.json` |
| `karsilastirma.html` | `karsilastirma.json` |
| `metodoloji.html` | `metodoloji.json` |

## Durum

- Faz 0 — iskelet kuruldu.
- Faz 1 — tamamlandı: `data/raw/` altında OGM (Ormancılık İstatistikleri
  2024) ve EFFIS/Copernicus resmi tabloları + 81 il GeoJSON. Kaynak ve
  bilinen sorunlar `data/raw/KAYNAKLAR.md`'de. Sadece birincil/resmi
  kaynaklar kullanılıyor, ikincil (haber/blog/STK) kaynak yok.
- Faz 2 — tamamlandı: `01_ingest.py` + `02_clean.py` çalışıyor, il adı
  eşleme ("Afyon" → "Afyonkarahisar"), tip dönüşümü, toplam tutarlılık
  kontrolleri `tests/test_clean.py` ile doğrulanıyor (6/6 geçiyor).
- Faz 3 — tamamlandı: `03_transform.py` ile hareketli ortalama, ortalama
  yangın büyüklüğü, neden oranları, il yoğunluk indeksi, ülke alan payları
  hesaplandı. Mevsimsellik ve "mega yangın" eşiği mevcut yıllık/il bazlı
  OGM verisiyle hesaplanamıyor (aylık/tekil kayıt yok) — not düşüldü.
  8/8 test geçiyor.
- Faz 4 — tamamlandı: `04_analyze.py` ile il/yıl sıralamaları ve uzun dönem
  eğim (1988-2024 tüm dönem vs. son 10 yıl), ülkeler arası Türkiye'nin
  konumu çıkarıldı. `05_export.py` ile `ozet.json`, `trend.json`,
  `cografi.json`, `nedenler.json`, `karsilastirma.json`, `metodoloji.json`
  üretildi ve `web/assets/data/` altına kopyalandı — bu şema artık sabit,
  site bu altı dosyayı okuyacak.
- Faz 5 — tamamlandı: site iskeleti kuruldu (`web/components/` header/
  footer, `loader.js`, `charts.js`, `style.css` — light/dark tema,
  dataviz paletinden vurgu/bağlam renkleri). Pilot sayfa `trend.html`
  baştan sona bitti: 3 çizgi grafik (yangın sayısı, yanan alan, ortalama
  büyüklük), her biri hareketli ortalama + tablo görünümü ile. `index.html`
  KPI kartlarıyla çalışıyor, `metodoloji.html` tam. `cografi.html`,
  `nedenler.html`, `karsilastirma.html` iskelet halinde (görselleştirme
  Faz 6'da). Playwright ile masaüstü+mobil ekran görüntüleri alındı,
  6 sayfada da konsol hatası yok.
- Faz 6 — tamamlandı: `cografi.html` Leaflet choropleth haritası (il
  yoğunluk indeksi, 5 kova, sıralı mavi skala) + en çok etkilenen 10 il
  tablosu. `nedenler.html` iki yığılmış alan grafiği (sayı payı, alan
  payı — 4 kategori, dataviz paletiyle doğrulanmış). `karsilastirma.html`
  "vurgu" desenli çok serili grafik: Türkiye vurgu renginde, 4 ülke
  bağlam grisinde. Üçü de Playwright ile masaüstü+koyu tema test edildi,
  konsol hatası yok.
- Faz 7 — tamamlandı: tüm sayfalar sayı-kaynak tutarlılığı için gözden
  geçirildi. İki sorun bulunup düzeltildi: (1) hesaplanan uzun dönem/son
  10 yıl eğilimi (`ozet.json`) hiçbir sayfada gösterilmiyordu — index.html'e
  KPI kartı eklendi; (2) "nedeni bilinmeyen" KPI'sı sayı mı alan mı
  bazında olduğunu belirtmiyordu — etiket netleştirildi. metodoloji.json'a
  EFFIS'in erken yıl veri boşluğu ve `ma_*` metrik ailesinin tam tanımı
  eklendi. HTML'de hardcoded istatistik olmadığı doğrulandı (tüm sayılar
  JSON'dan geliyor).
- Faz 8 — tamamlandı: GitHub'da public repo (`Simge-bit/orman-yanginlari`)
  oluşturuldu, GitHub Pages "GitHub Actions" kaynağıyla etkinleştirildi.
  `.github/workflows/pages.yml` her `main` push'unda pipeline'ı çalıştırıp
  testleri geçirip `web/`'i yayınlıyor. CI'da bir gerçek hata bulundu ve
  düzeltildi: `data/interim`/`data/processed` .gitignore'da olduğu için
  temiz bir clone'da hiç yoktu, `utils.py`'nin `data_path()`'i artık
  yazmadan önce klasörü oluşturuyor. Site canlıda Playwright ile uçtan
  uca test edildi, 6 sayfa da hatasız.

Proje tamamlandı: veri toplamadan (Faz 1) canlı siteye (Faz 8) kadar tüm
fazlar bitti. Veri güncellemek için `data/raw/`'ı değiştirip `main`'e push
yeterli — CI pipeline'ı otomatik çalıştırıp siteyi günceller.

**Sonradan eklenenler (2026-07-31):**
- 2025 yılı ulusal rakamları eklendi (OGM'nin "Ormancılık İstatistikleri"
  yıllığının 2025 sürümü henüz yayınlanmadığı için ayrı bir resmi kaynaktan,
  "2025 Faaliyet Raporu"ndan). Site artık en güncel yılı otomatik gösteriyor
  — sayfa başlıkları yıl aralığını veriden dinamik okuyor, elle
  güncellenmesi gerekmiyor.
- `cografi.html`'e NASA FIRMS/VIIRS tabanlı canlı sıcak nokta katmanı
  eklendi (yukarıya bkz.) — GitHub Actions'ta 3 saatte bir otomatik
  tazeleniyor.
