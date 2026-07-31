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

İl adı kendi tr_iller.geojson'umuzdan (nokta-içinde-poligon) geliyor — bu
her zaman çalışır. İlçe/köy adı için OpenStreetMap Nominatim'in ücretsiz
reverse-geocoding servisi kullanılıyor; bu servisin kullanım politikası
saniyede en fazla 1 istek ve tanımlayıcı bir User-Agent gerektiriyor, bu
yüzden yakın noktalar (aynı ~1km hücre) tek sorguda gruplanıyor ve toplam
sorgu sayısı sabit bir tavanla sınırlanıyor — büyük bir yangında yüzlerce
nokta gelse bile servise aşırı yüklenilmiyor.
"""
import json
import os
import shutil
import time
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

NOMINATIM_KULLANICI_ARACI = "orman-yanginlari-site/1.0 (kisisel/politik veri sitesi; iletisim: repo issue)"
NOMINATIM_MAX_SORGU = 60  # aşırı yangın günlerinde bile Nominatim'e nazik davranmak için tavan
NOMINATIM_HUCRE_ONDALIK = 2  # ~1.1 km — yakın noktaları tek sorguda grupla

KOY_ALANLARI = ["hamlet", "village", "neighbourhood", "suburb", "quarter"]
ILCE_ALANLARI = ["town", "municipality", "city_district", "county"]


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


def _yer_metni(address: dict) -> str | None:
    koy = next((address[a] for a in KOY_ALANLARI if a in address), None)
    ilce = next((address[a] for a in ILCE_ALANLARI if a in address), None)
    parcalar = [p for p in [koy, ilce] if p]
    return ", ".join(parcalar) if parcalar else None


def _ilce_koy_bul(lat: float, lon: float) -> str | None:
    try:
        yanit = requests.get(
            "https://nominatim.openstreetmap.org/reverse",
            params={"lat": lat, "lon": lon, "format": "jsonv2", "accept-language": "tr", "zoom": 14},
            headers={"User-Agent": NOMINATIM_KULLANICI_ARACI},
            timeout=10,
        )
        if not yanit.ok:
            return None
        return _yer_metni(yanit.json().get("address", {}))
    except requests.RequestException:
        return None


def _ilce_koy_ekle(noktalar: list[dict]) -> None:
    hucreler: dict[tuple, str | None] = {}
    sorgu_sayaci = 0

    for nokta in noktalar:
        hucre = (round(nokta["latitude"], NOMINATIM_HUCRE_ONDALIK), round(nokta["longitude"], NOMINATIM_HUCRE_ONDALIK))
        if hucre not in hucreler:
            if sorgu_sayaci >= NOMINATIM_MAX_SORGU:
                hucreler[hucre] = None
                continue
            hucreler[hucre] = _ilce_koy_bul(nokta["latitude"], nokta["longitude"])
            sorgu_sayaci += 1
            time.sleep(1)  # Nominatim kullanım politikası: saniyede en fazla 1 istek
        nokta["yer"] = hucreler[hucre]

    print(f"[hotspots] {sorgu_sayaci} benzersiz konum Nominatim'e soruldu ({len(noktalar)} nokta için)")


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

    if noktalar:
        _ilce_koy_ekle(noktalar)

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
