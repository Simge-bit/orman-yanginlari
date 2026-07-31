# Türkiye Orman Yangınları — Veri Analizi ve Site

Türkiye'deki orman yangınlarına dair kamuya açık verilerin (OGM, EFFIS, TÜİK)
temizlenip analiz edildiği ve sonuçların statik bir çok sayfalı web sitesinde
sunulduğu proje.

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

Faz 0 — iskelet kuruldu. Sıradaki adım: Faz 1, veri toplama
(`data/raw/` içine OGM/EFFIS/TÜİK kaynaklarının indirilmesi).
