"""NASA FIRMS'ten (VIIRS uydu verisi) Türkiye sınırları içindeki son 24
saatlik sıcak nokta (aktif yangın adayı) tespitlerini çeker.

Bu, 01-05 arası tarihsel/istatistiksel pipeline'ın bir parçası DEĞİLDİR —
bağımsız çalışır, GitHub Actions'ta hem push'ta hem zamanlanmış (cron)
olarak tetiklenir ki harita "canlı" kalsın. FIRMS API'sinin CORS desteği
olmadığı için tarayıcıdan doğrudan çağrılamıyor — bu yüzden veri burada,
sunucu tarafında (CI) çekilip statik JSON'a gömülüyor.

Gerekli: FIRMS_MAP_KEY ortam değişkeni (ücretsiz anahtar:
https://firms.modaps.eosdis.nasa.gov/api/map_key/). Anahtar yoksa script
sessizce atlanır (yerel geliştirmede bu adımı zorunlu kılmamak için).
"""
import json
import os
import shutil
from datetime import datetime, timezone
from io import StringIO

import pandas as pd
import requests
from shapely.geometry import Point, shape
from shapely.ops import unary_union

from utils import ROOT, data_path

TURKIYE_BBOX = "25,35,45,43"  # west,south,east,north — Türkiye + yakın çevresi
KAYNAK_SENSORU = "VIIRS_SNPP_NRT"
GUN_ARALIGI = 1
DUSUK_GUVEN_HARIC = True  # VIIRS confidence='l' (low) kayıtlarını çıkar


def _yaz(veri: dict) -> None:
    processed_path = data_path("processed", "hotspots.json")
    with open(processed_path, "w", encoding="utf-8") as f:
        json.dump(veri, f, ensure_ascii=False, indent=2)

    web_dir = ROOT / "web" / "assets" / "data"
    web_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy(processed_path, web_dir / "hotspots.json")


def _turkiye_sinirini_yukle():
    geo = json.load(open(data_path("raw", "tr_iller.geojson"), encoding="utf-8"))
    poligonlar = [shape(f["geometry"]) for f in geo["features"]]
    return unary_union(poligonlar)


def main():
    map_key = os.environ.get("FIRMS_MAP_KEY")
    if not map_key:
        print("[hotspots] FIRMS_MAP_KEY tanımlı değil, bu adım atlanıyor (yerel geliştirmede normal).")
        return

    url = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{map_key}/{KAYNAK_SENSORU}/{TURKIYE_BBOX}/{GUN_ARALIGI}"
    yanit = requests.get(url, timeout=30)
    yanit.raise_for_status()

    metin = yanit.text.strip()
    guncelleme_zamani = datetime.now(timezone.utc).isoformat()

    if not metin or metin.lower().startswith("invalid") or "latitude" not in metin.splitlines()[0]:
        print(f"[hotspots] UYARI: FIRMS API beklenmeyen yanıt döndü: {metin[:200]!r}")
        _yaz({"guncelleme_zamani": guncelleme_zamani, "kaynak": KAYNAK_SENSORU, "nokta_sayisi": 0, "noktalar": []})
        return

    df = pd.read_csv(StringIO(metin))
    if DUSUK_GUVEN_HARIC and "confidence" in df.columns:
        df = df[df["confidence"] != "l"]

    if len(df):
        sinir = _turkiye_sinirini_yukle()
        icinde = df.apply(lambda satir: sinir.contains(Point(satir["longitude"], satir["latitude"])), axis=1)
        df = df[icinde]

    kolonlar = [k for k in ["latitude", "longitude", "acq_date", "acq_time", "confidence", "frp"] if k in df.columns]
    noktalar = df[kolonlar].to_dict(orient="records")

    _yaz({
        "guncelleme_zamani": guncelleme_zamani,
        "kaynak": f"NASA FIRMS, {KAYNAK_SENSORU}",
        "gun_araligi": GUN_ARALIGI,
        "nokta_sayisi": len(noktalar),
        "noktalar": noktalar,
    })
    print(f"[hotspots] {len(noktalar)} sıcak nokta (Türkiye sınırları içinde, son {GUN_ARALIGI} gün)")


if __name__ == "__main__":
    main()
