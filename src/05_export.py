"""Analiz katmanının son adımı: her site sayfası için JSON üretir ve
web/assets/data/ altına kopyalar. Buradaki şema analiz ile sunum arasındaki
sözleşmedir — alan adları burada dondurulur, web/ katmanı sadece bunları okur.
"""
import json
import shutil

import pandas as pd

from utils import data_path, load_config, ROOT

NEDEN_KATEGORILERI = ["kasit", "ihmal_kaza", "dogal", "bilinmeyen"]
WEB_DATA_DIR = ROOT / "web" / "assets" / "data"


def _yaz(ad: str, veri) -> None:
    processed_path = data_path("processed", f"{ad}.json")
    processed_path.parent.mkdir(parents=True, exist_ok=True)
    with open(processed_path, "w", encoding="utf-8") as f:
        json.dump(veri, f, ensure_ascii=False, indent=2, allow_nan=False)

    WEB_DATA_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy(processed_path, WEB_DATA_DIR / f"{ad}.json")
    print(f"[export] {ad}.json yazıldı")


def export_ozet():
    yillik = pd.read_csv(data_path("interim", "yillik_metrikler.csv")).sort_values("yil")
    egim = pd.read_csv(data_path("interim", "yillik_egim.csv"))
    il_siralama = pd.read_csv(data_path("interim", "il_siralama.csv"))
    yogunlasma = pd.read_csv(data_path("interim", "yogunlasma.csv")).iloc[0]

    son = yillik.iloc[-1]
    onceki = yillik.iloc[-2]
    en_buyuk_yil = yillik.loc[yillik["yanan_alan_ha"].idxmax()]
    en_cok_etkilenen_il = il_siralama.iloc[0]
    tum_donem_egim = egim.iloc[0]
    son_10_yil_egim = egim.iloc[1]

    veri = {
        "son_yil": int(son["yil"]),
        "son_yil_yangin_sayisi": int(son["yangin_sayisi"]),
        "son_yil_yanan_alan_ha": float(son["yanan_alan_ha"]),
        "son_yil_ortalama_buyukluk_ha": round(float(son["ortalama_buyukluk_ha"]), 2),
        "onceki_yila_gore_sayi_degisim_yuzde": round(float(son["yangin_sayisi"] / onceki["yangin_sayisi"] * 100 - 100), 1),
        "onceki_yila_gore_alan_degisim_yuzde": round(float(son["yanan_alan_ha"] / onceki["yanan_alan_ha"] * 100 - 100), 1),
        "en_buyuk_yil": {"yil": int(en_buyuk_yil["yil"]), "yanan_alan_ha": float(en_buyuk_yil["yanan_alan_ha"])},
        "en_cok_etkilenen_il_2024": {
            "il": en_cok_etkilenen_il["il"],
            "yanan_alan_ha": float(en_cok_etkilenen_il["yanan_alan_ha"]),
        },
        "bilinmeyen_neden_orani_son_yil_yuzde": round(float(son["bilinmeyen_sayi_oran"]), 1),
        "uzun_donem_egim_ha_yil": {"kapsam": tum_donem_egim["kapsam"], "deger": round(float(tum_donem_egim["alan_egimi_ha_yil"]), 1)},
        "son_10_yil_egim_ha_yil": {"kapsam": son_10_yil_egim["kapsam"], "deger": round(float(son_10_yil_egim["alan_egimi_ha_yil"]), 1)},
        "kapsam_yil_araligi": [int(yillik["yil"].min()), int(yillik["yil"].max())],
        "yogunlasma": {
            "en_kotu_yil_sayisi": int(yogunlasma["en_kotu_yil_sayisi"]),
            "en_kotu_yillar": yogunlasma["en_kotu_yillar"],
            "orani_yuzde": float(yogunlasma["en_kotu_yillar_orani_yuzde"]),
            "toplam_yil_sayisi": int(yogunlasma["toplam_yil_sayisi"]),
        },
    }
    _yaz("ozet", veri)


def export_trend():
    df = pd.read_csv(data_path("interim", "yillik_metrikler.csv")).sort_values("yil")
    kolonlar = [
        "yil", "yangin_sayisi", "yanan_alan_ha", "ortalama_buyukluk_ha",
        "ma_yangin_sayisi", "ma_yanan_alan_ha", "ma_ortalama_buyukluk_ha",
    ]
    df["yil"] = df["yil"].astype(int)
    kayitlar = json.loads(df[kolonlar].round(2).to_json(orient="records"))
    _yaz("trend", {"yillik": kayitlar})


def export_cografi():
    df = pd.read_csv(data_path("interim", "il_siralama.csv"))
    orman_kaplama_df = pd.read_csv(data_path("interim", "orman_alani_il.csv"))[["il", "orman_kaplama_yuzde"]]
    df = df.merge(orman_kaplama_df, on="il", how="left")
    kolonlar = [
        "il", "yangin_sayisi", "yanan_alan_ha", "orman_alani_ha", "orman_kaplama_yuzde",
        "yogunluk_indeksi_yuzde", "sira_alan", "sira_yogunluk",
    ]
    kayitlar = json.loads(df[kolonlar].round(3).to_json(orient="records"))

    bolge_df = pd.read_csv(data_path("interim", "bolge_siralama_2025.csv"))
    bolge_kayitlar = json.loads(bolge_df[["bolge_muduru", "yangin_sayisi", "yanan_alan_ha", "sira_alan"]].round(2).to_json(orient="records"))

    bolge_neden_df = pd.read_csv(data_path("interim", "bolge_neden_siralama_2025.csv"))
    bolge_neden_kolonlar = [
        "bolge_muduru", "yangin_sayisi", "kasit_sayi_oran", "kasit_alan_oran",
        "sira_kasit_alan_oran", "sira_kasit_sayi_oran",
    ]
    bolge_neden_kayitlar = json.loads(bolge_neden_df[bolge_neden_kolonlar].round(2).to_json(orient="records"))

    korelasyon = pd.read_csv(data_path("interim", "korelasyon.csv")).iloc[0]

    _yaz("cografi", {
        "yil": 2024,
        "kapsam_notu": "il bazında sadece 2024 verisi mevcut",
        "iller": kayitlar,
        "orman_kaplama_korelasyonu": {
            "pearson_r": float(korelasyon["pearson_r"]),
            "il_sayisi": int(korelasyon["il_sayisi"]),
            "aciklama": (
                "Orman kaplama oranı (%) ile yangın yoğunluk indeksi arasındaki "
                "Pearson korelasyon katsayısı. |r| < 0,3 zayıf/anlamsız bir ilişki "
                "olduğunu gösterir — yani daha ormanlık iller orantılı olarak daha "
                "çok yanmıyor; konum, iklim ve insan etkeni daha belirleyici olabilir."
            ),
        },
        "bolge_2025": {
            "yil": 2025,
            "kapsam_notu": (
                "İl bazında 2025 verisi hiçbir resmi kaynakta yok. Bu, OGM'nin 2025 "
                "Faaliyet Raporu'ndaki tek coğrafi kırılım — 'Orman Bölge Müdürlüğü' "
                "il ile birebir örtüşmeyen ayrı bir idari birimdir (bazı bölgeler "
                "birden fazla ili kapsar)."
            ),
            "bolgeler": bolge_kayitlar,
            "kasit_orani_siralama": {
                "kapsam_notu": "En az 15 yangını olan bölge müdürlükleri arasında, kasıt (kundaklama) payı en yüksek olanlar.",
                "bolgeler": bolge_neden_kayitlar,
            },
        },
    })


def export_nedenler():
    df = pd.read_csv(data_path("interim", "yillik_metrikler.csv")).sort_values("yil")
    df = df[df["neden_kirilimi_var"]]
    kolonlar = ["yil"] + [f"{k}_{t}_oran" for k in NEDEN_KATEGORILERI for t in ("sayi", "alan")]
    df["yil"] = df["yil"].astype(int)
    kayitlar = json.loads(df[kolonlar].round(2).to_json(orient="records"))

    egim_df = pd.read_csv(data_path("interim", "neden_egimi.csv"))
    egim_kayitlar = json.loads(
        egim_df[["kategori", "sayi_oran_egimi_puan_yil", "alan_oran_egimi_puan_yil"]].round(3).to_json(orient="records")
    )

    _yaz("nedenler", {
        "kapsam_notu": "1997 öncesi neden kırılımı OGM tarafından yayınlanmamış",
        "yillik": kayitlar,
        "egim": {
            "kapsam": egim_df.iloc[0]["kapsam"],
            "kategoriler": egim_kayitlar,
        },
    })


def export_karsilastirma():
    df = pd.read_csv(data_path("interim", "ulke_siralama.csv")).sort_values(["yil", "ulke"])
    kolonlar = ["yil", "ulke", "yanan_alan_ha", "yangin_sayisi", "ortalama_buyukluk_ha", "alan_payi_yuzde", "sira_alan"]
    df["yil"] = df["yil"].astype(int)
    kayitlar = json.loads(df[kolonlar].where(df[kolonlar].notna(), None).to_json(orient="records"))
    _yaz("karsilastirma", {"ulkeler": kayitlar})


def export_metodoloji(config: dict):
    yillik = pd.read_csv(data_path("interim", "yillik_seri.csv"))
    gercek_yil_araligi = [int(yillik["yil"].min()), int(yillik["yil"].max())]

    veri = {
        "kaynaklar": [
            {"ad": "OGM Ormancılık İstatistikleri 2024", "kurum": config["kaynaklar"]["ogm"]},
            {"ad": "OGM 2025 Faaliyet Raporu (sadece son yıl için)", "kurum": config["kaynaklar"].get("ogm_faaliyet_2025", "")},
            {"ad": "EFFIS/Copernicus ülke karşılaştırma raporu", "kurum": config["kaynaklar"]["effis"]},
            {"ad": "81 il sınırı (GeoJSON)", "kurum": config["kaynaklar"]["geojson"]},
            {"ad": "Canlı sıcak nokta katmanı (cografi.html)", "kurum": "NASA FIRMS (VIIRS uydu verisi), https://firms.modaps.eosdis.nasa.gov/ — istatistik değil, ham gözlem verisi"},
            {"ad": "Sıcak noktaların ilçe/köy adı (cografi.html)", "kurum": "OpenStreetMap Nominatim, https://nominatim.openstreetmap.org — resmi bir istatistik kaynağı değil, topluluk kaynaklı yer-adı sorgu servisi; sadece konum etiketlemek için kullanılıyor, hiçbir sayı bu kaynaktan gelmiyor"},
        ],
        "metrikler": [
            {"id": "ortalama_buyukluk_ha", "tanim": "Yanan alan (ha) / yangın sayısı", "birim": "hektar/yangın"},
            {"id": "ma_yangin_sayisi / ma_yanan_alan_ha / ma_ortalama_buyukluk_ha", "tanim": f"İlgili metriğin {config['hareketli_ort_penceresi']} yıllık hareketli ortalaması", "birim": "metriğin kendi birimi"},
            {"id": "yogunluk_indeksi_yuzde", "tanim": "İl bazında yanan alan / toplam orman alanı", "birim": "%"},
            {"id": "*_sayi_oran / *_alan_oran", "tanim": "Neden kategorisinin o yılki toplam içindeki payı (kasıt/ihmal-kaza/doğal/bilinmeyen)", "birim": "%"},
            {"id": "alan_payi_yuzde", "tanim": "Ülkenin, o yıl karşılaştırma grubundaki (5 ülke) toplam yanan alan içindeki payı", "birim": "%"},
            {"id": "yogunlasma.orani_yuzde", "tanim": "En kötü 5 yılın, tüm dönemin toplam yanan alanı içindeki payı", "birim": "%"},
            {"id": "orman_kaplama_korelasyonu.pearson_r", "tanim": "İl bazında orman kaplama oranı (%) ile yoğunluk indeksi arasındaki Pearson korelasyon katsayısı", "birim": "-1 ile 1 arası"},
            {"id": "kasit_orani_siralama.kasit_alan_oran / kasit_sayi_oran", "tanim": "Bölge müdürlüğü başına kasıt (kundaklama) kaynaklı yangınların payı, en az 15 yangınlık bölgeler arasında", "birim": "%"},
            {"id": "nedenler.egim.*_oran_egimi_puan_yil", "tanim": "Neden kategorisinin (kasıt/ihmal-kaza/doğal/bilinmeyen) yıllık payındaki doğrusal eğilim (basit doğrusal regresyon eğimi)", "birim": "yüzde puan/yıl"},
        ],
        "kapsam": {
            "yil_araligi": gercek_yil_araligi,
            "il_bazinda_yil": 2024,
            "karsilastirma_ulkeleri": config["karsilastirma_ulkeler"],
        },
        "bilinen_sinirlamalar": [
            "Mevsimsellik hesaplanamadı: OGM'nin yıllık istatistik yayınında aylık kırılım yok.",
            f"'Mega yangın' eşiği (config: {config['esikler']['mega_yangin_ha']} ha) uygulanamadı: mevcut veri yıllık/il toplamları düzeyinde, tekil yangın kaydı yok.",
            "İl bazında kırılım sadece 2024 için mevcut; çok yıllı il serisi yok. En güncel yıl için il bazında resmi veri yok — bunun yerine 'Orman Bölge Müdürlüğü' (il ile birebir örtüşmeyen ayrı bir idari birim) düzeyinde bir tablo eklendi (cografi.html, cografi.json bolge_2025).",
            "En güncel yıl (bkz. kapsam) 'Ormancılık İstatistikleri' yıllığından değil, OGM'nin 2025 Faaliyet Raporu'ndan (Tablo 16/17) alındı — yıllık istatistik yayınının o yılki sürümü erişim tarihinde henüz yayınlanmamıştı. Bu iki OGM yayını, aynı yıllar için neden kategorileri arasında (toplamlar aynı kalsa da) küçük dağılım farkları taşıyabiliyor.",
            "EFFIS ülke karşılaştırması en güncel yılı içermiyor: EFFIS'in ilgili yıla ait raporu erişim tarihinde henüz yayınlanmamıştı.",
            "2013 yılı için OGM kaynağının kendi tablosunda ~0.5 ha'lık küçük bir yuvarlama farkı var (neden kırılımı toplamı ile yıl toplamı arasında).",
            "GeoJSON'da 'Afyon', OGM tablolarında 'Afyonkarahisar' olarak geçiyor; eşleme pipeline'da yapılıyor (bkz. src/utils.py IL_ALIASLARI).",
            "EFFIS ülke karşılaştırmasında bazı ülkeler erken yıllarda (1980'ler) veri bildirmemiş; grafikte ve tabloda bu yıllar boşluk olarak görünür.",
            "Bölge müdürlüğü bazında 2025 neden kırılımı (Ek 6), ulusal tablonun 4 kategorisinden farklı olarak İhmal ve Kaza'yı ayrı sütunlarda veriyor; siteyle tutarlı olsun diye ikisi 'ihmal_kaza' olarak toplanıyor. Kasıt oranı sıralaması, tesadüfen çarpık oran çıkmasın diye en az 15 yangınlık bölgelerle sınırlı.",
            "Orman kaplama % ile yoğunluk indeksi arasındaki korelasyon sadece 2024 kesitinde (81 il, tek yıl) hesaplandı — zaman içindeki değişimi yakalamaz, sadece o yılki iller-arası ilişkiyi gösterir.",
            "Neden payı eğilimi (nedenler.egim) tek bir doğrusal eğim özetidir; yıldan yıla dalgalanmayı veya eğilimin yön değiştirdiği dönemleri yakalamaz. Sadece neden kırılımı yayınlanan yıllar (1997+) dahil edildi.",
            "Tüm istatistiksel rakamlar (yangın sayısı, alan, oran) birincil/resmi kaynaklardan (OGM, EFFIS) gelir; haber/blog/STK derlemesi istatistik kaynağı olarak alınmadı. Canlı harita katmanı (NASA FIRMS) ve yer adı etiketleme (OpenStreetMap Nominatim) bu kuralın istisnası değil ama farklı bir kategoridir: ilki ham gözlem verisi, ikincisi sadece görüntüleme amaçlı yer-adı sorgusu — hiçbiri istatistiksel bir iddia taşımıyor.",
        ],
        "olusturulma_notu": "Bu dosya src/05_export.py tarafından otomatik üretilir, elle düzenlenmez.",
    }
    _yaz("metodoloji", veri)


def export_geojson():
    kaynak = data_path("raw", "tr_iller.geojson")
    shutil.copy(kaynak, WEB_DATA_DIR / "tr_iller.geojson")
    print("[export] tr_iller.geojson web/assets/data/ altına kopyalandı")


def main():
    config = load_config()
    export_ozet()
    export_trend()
    export_cografi()
    export_nedenler()
    export_karsilastirma()
    export_metodoloji(config)
    export_geojson()


if __name__ == "__main__":
    main()
