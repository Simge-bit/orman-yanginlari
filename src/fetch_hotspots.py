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

from utils import ROOT, data_path, standardize_il

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


def _il_poligonlarini_yukle():
    geo = json.load(open(data_path("raw", "tr_iller.geojson"), encoding="utf-8"))
    return [(standardize_il(f["properties"]["name"]), shape(f["geometry"])) for f in geo["features"]]


def _il_bul(nokta: Point, il_poligonlari) -> str:
    # Önce tam içinde olduğu ili ara; sınır/topoloji boşluğuna denk gelirse
    # (bkz. KAYNAKLAR.md — GeoJSON kaynağı OSM türevi, komşu iller arasında
    # küçük boşluklar olabiliyor) en yakın ile düşer.
    for il_adi, poligon in il_poligonlari:
        if poligon.contains(nokta):
            return il_adi
    en_yakin_il, en_yakin_mesafe = None, None
    for il_adi, poligon in il_poligonlari:
        mesafe = poligon.distance(nokta)
        if en_yakin_mesafe is None or mesafe < en_yakin_mesafe:
            en_yakin_il, en_yakin_mesafe = il_adi, mesafe
    return en_yakin_il


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

    noktalar = []
    if len(df):
        il_poligonlari = _il_poligonlarini_yukle()
        sinir = unary_union([p for _, p in il_poligonlari])

        for _, satir in df.iterrows():
            nokta = Point(float(satir["longitude"]), float(satir["latitude"]))
            if not sinir.contains(nokta):
                continue
            noktalar.append({
                "latitude": float(satir["latitude"]),
                "longitude": float(satir["longitude"]),
                "acq_date": str(satir.get("acq_date", "")),
                "acq_time": int(satir.get("acq_time", 0)),
                "confidence": str(satir.get("confidence", "")),
                "frp": float(satir["frp"]) if "frp" in satir and pd.notna(satir["frp"]) else None,
                "il": _il_bul(nokta, il_poligonlari),
            })

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
