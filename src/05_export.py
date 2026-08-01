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
    son_donem = pd.read_csv(data_path("interim", "son_donem_karsilastirmasi.csv")).iloc[0]

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
        "son_donem_karsilastirmasi": {
            "son_donem_kapsam": son_donem["son_donem_kapsam"],
            "son_donem_yil_sayisi": int(son_donem["son_donem_yil_sayisi"]),
            "son_donem_toplam_alan_ha": float(son_donem["son_donem_toplam_alan_ha"]),
            "son_donem_toplam_yangin_sayisi": int(son_donem["son_donem_toplam_yangin_sayisi"]),
            "son_donem_alan_orani_yuzde": float(son_donem["son_donem_alan_orani_yuzde"]),
            "onceki_donem_kapsam": son_donem["onceki_donem_kapsam"],
            "onceki_donem_yil_sayisi": int(son_donem["onceki_donem_yil_sayisi"]),
            "onceki_donem_toplam_alan_ha": float(son_donem["onceki_donem_toplam_alan_ha"]),
            "onceki_donem_toplam_yangin_sayisi": int(son_donem["onceki_donem_toplam_yangin_sayisi"]),
            "ortalama_yillik_alan_kati": float(son_donem["ortalama_yillik_alan_kati"]),
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

    silvikultur_bilesenleri = [
        "zarar_gormeyen_ha", "dogal_genclestirme_ha", "suni_genclestirme_ha",
        "rehabilitasyon_ha", "agaclandirma_ha", "koruma_ha", "gelecek_yillara_ha",
    ]
    silvikultur_ulusal = pd.read_csv(data_path("interim", "silvikultur_2024_ulusal.csv")).iloc[0]
    silvikultur_siralama_df = pd.read_csv(data_path("interim", "silvikultur_siralama_2024.csv"))
    silvikultur_kolonlar = ["bolge_muduru", "toplam_alan_ha"] + silvikultur_bilesenleri + ["gelecek_yillara_ha_oran", "sira_gelecek_yillara_oran"]
    silvikultur_bolge_kayitlar = json.loads(
        silvikultur_siralama_df[silvikultur_kolonlar].round(2).to_json(orient="records")
    )

    bolge_egim_df = pd.read_csv(data_path("interim", "bolge_cok_yillik_egim.csv")).sort_values("egim_ha_yil", ascending=False)
    bolge_egim_kayitlar = json.loads(
        bolge_egim_df[["bolge_muduru", "kapsam", "veri_yil_sayisi", "egim_ha_yil", "toplam_ha", "ortalama_yillik_ha"]]
        .round(1).to_json(orient="records")
    )

    vasif_ulusal = pd.read_csv(data_path("interim", "vasif_dagilimi_2024_ulusal.csv")).iloc[0]
    vasif_siralama_df = pd.read_csv(data_path("interim", "vasif_siralama_2024.csv"))
    vasif_kayitlar = json.loads(vasif_siralama_df.round(1).to_json(orient="records"))

    egim_kasit_ozet = pd.read_csv(data_path("interim", "bolge_egim_kasit_korelasyonu.csv")).iloc[0]
    egim_kasit_veri = pd.read_csv(data_path("interim", "bolge_egim_kasit_veri.csv"))
    egim_kasit_noktalar = json.loads(
        egim_kasit_veri[["bolge_muduru", "egim_ha_yil", "kasit_alan_oran"]].round(2).to_json(orient="records")
    )

    _yaz("cografi", {
        "yil": 2024,
        "kapsam_notu": "il bazında sadece 2024 verisi mevcut",
        "iller": kayitlar,
        "orman_kaplama_korelasyonu": {
            "pearson_r": float(korelasyon["pearson_r"]),
            "p_degeri": float(korelasyon["p_degeri"]),
            "anlamli_mi": bool(korelasyon["anlamli_mi"]),
            "il_sayisi": int(korelasyon["il_sayisi"]),
            "aciklama": (
                "Orman kaplama oranı (%) ile yangın yoğunluk indeksi arasındaki Pearson "
                "korelasyon katsayısı ve anlamlılık testi (p-değeri, α=0,05). "
                + ("İstatistiksel olarak anlamlı bir ilişki bulundu." if korelasyon["anlamli_mi"]
                   else "İlişki istatistiksel olarak anlamlı değil — yani daha ormanlık iller "
                        "orantılı olarak daha çok yanmıyor; konum, iklim ve insan etkeni daha "
                        "belirleyici olabilir.")
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
        "silvikultur_2024": {
            "yil": 2024,
            "kapsam_notu": (
                "OGM Tablo 2.18: 2024'te yanan alanın (Orman Bölge Müdürlüğü bazında, "
                "Milli Parklar hariç) hangi işleme alındığı. 'Ağaçlandırma programına alınan' "
                "ve 'gençleştirme' aktif müdahaleyi, 'gelecek yıllara bırakılan' ise henüz "
                "hiçbir işlem yapılmadığını gösterir."
            ),
            "ulusal": {
                "toplam_alan_ha": float(silvikultur_ulusal["toplam_alan_ha"]),
                **{k: float(silvikultur_ulusal[k]) for k in silvikultur_bilesenleri},
                **{f"{k}_oran": round(float(silvikultur_ulusal[f"{k}_oran"]), 1) for k in silvikultur_bilesenleri},
            },
            "bolgeler_siralama": {
                "kapsam_notu": "En az 50 hektarlık bölge müdürlükleri arasında, 'gelecek yıllara bırakılan' alan payı en yüksek olanlar.",
                "bolgeler": silvikultur_bolge_kayitlar,
            },
        },
        "bolge_egim_2004_2024": {
            "kapsam_notu": (
                "OGM Tablo 2.12/2.13: her bölge müdürlüğünün (DKMPGM dahil) 2004-2024 arası kendi "
                "yanan alan serisindeki doğrusal eğilimi (basit doğrusal regresyon eğimi). En az "
                "10 yıllık veri şartı arandı."
            ),
            "bolgeler": bolge_egim_kayitlar,
        },
        "vasif_dagilimi_2024": {
            "yil": 2024,
            "kapsam_notu": "OGM Tablo 2.17: 2024'te yanan alanın orman türüne (vasfına) göre dağılımı.",
            "toplam_alan_ha": float(vasif_ulusal["toplam_ha"]),
            "kategoriler": vasif_kayitlar,
        },
        "bolge_egim_kasit_korelasyonu": {
            "kapsam_notu": (
                "Bölgenin 2004-2024 arası yanan alan eğilimi (egim_ha_yil) ile 2025 kasıt "
                "(kundaklama) oranı arasındaki ilişki, en az 15 yangınlık bölgeler arasında."
            ),
            "n_tum": int(egim_kasit_ozet["n_tum"]),
            "r_tum": round(float(egim_kasit_ozet["r_tum"]), 3),
            "p_tum": round(float(egim_kasit_ozet["p_tum"]), 4),
            "uc_noktalar": egim_kasit_ozet["uc_noktalar"],
            "n_haric": int(egim_kasit_ozet["n_haric"]),
            "r_haric": round(float(egim_kasit_ozet["r_haric"]), 3),
            "p_haric": round(float(egim_kasit_ozet["p_haric"]), 4),
            "aciklama": (
                "Tüm bölgelerde ilişki güçlü ve anlamlı görünüyor, ama bu neredeyse tamamen "
                "Muğla ve Antalya'dan (hem en hızlı kötüleşen hem en yüksek kasıt oranına "
                "sahip iki bölge) kaynaklanıyor — bu ikisi çıkarıldığında ilişki kayboluyor. "
                "Yani bu, kasıtın ulusal düzeyde kötüleşmeyi açıkladığı anlamına gelmez; "
                "sadece bu iki bölgeye özgü çarpıcı bir örtüşmedir."
            ),
            "noktalar": egim_kasit_noktalar,
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

    alt_kategori_df = pd.read_csv(data_path("interim", "neden_alt_kategori_siralama_2024.csv"))
    alt_kategori_kayitlar = json.loads(alt_kategori_df.round(1).to_json(orient="records"))
    ulusal_2024 = pd.read_csv(data_path("interim", "neden_bolge_2024_ulusal.csv")).iloc[0]

    _yaz("nedenler", {
        "kapsam_notu": "1997 öncesi neden kırılımı OGM tarafından yayınlanmamış",
        "yillik": kayitlar,
        "egim": {
            "kapsam": egim_df.iloc[0]["kapsam"],
            "kategoriler": egim_kayitlar,
        },
        "alt_kategori_2024": {
            "kapsam_notu": (
                "OGM Tablo 2.15/2.16: 2024'te yangınların çıkış nedeni, ulusal 4 kategoriden "
                "(kasıt/ihmal-kaza/doğal/bilinmeyen) çok daha ince ayrıştırılmış. Bu kırılımın "
                "2025 sürümü henüz yayınlanmadı (yıllık istatistik kitabının bir tablosu, "
                "2025 Faaliyet Raporu'nda bu düzeyde ayrıntı yok)."
            ),
            "toplam_alan_ha": float(ulusal_2024["toplam_ha"]),
            "toplam_sayi": float(ulusal_2024["toplam_sayi"]),
            "kategoriler": alt_kategori_kayitlar,
        },
    })


def export_karsilastirma():
    df = pd.read_csv(data_path("interim", "ulke_siralama.csv")).sort_values(["yil", "ulke"])
    kolonlar = ["yil", "ulke", "yanan_alan_ha", "yangin_sayisi", "ortalama_buyukluk_ha", "alan_payi_yuzde", "sira_alan"]
    df["yil"] = df["yil"].astype(int)
    kayitlar = json.loads(df[kolonlar].where(df[kolonlar].notna(), None).to_json(orient="records"))

    egim_df = pd.read_csv(data_path("interim", "ulke_egim.csv")).sort_values("egim_ha_yil", ascending=False)
    egim_kayitlar = json.loads(
        egim_df[["ulke", "kapsam", "veri_yil_sayisi", "egim_ha_yil"]].round(1).to_json(orient="records")
    )

    _yaz("karsilastirma", {"ulkeler": kayitlar, "ulke_egimleri": egim_kayitlar})


def export_metodoloji(config: dict):
    yillik = pd.read_csv(data_path("interim", "yillik_seri.csv"))
    gercek_yil_araligi = [int(yillik["yil"].min()), int(yillik["yil"].max())]

    veri = {
        "kaynaklar": [
            {"ad": "OGM Ormancılık İstatistikleri 2024", "kurum": config["kaynaklar"]["ogm"]},
            {"ad": "OGM 2025 Faaliyet Raporu (sadece son yıl için)", "kurum": config["kaynaklar"].get("ogm_faaliyet_2025", "")},
            {"ad": "EFFIS/Copernicus ülke karşılaştırma raporu", "kurum": config["kaynaklar"]["effis"]},
            {"ad": "81 il sınırı (GeoJSON)", "kurum": config["kaynaklar"]["geojson"]},
            {"ad": "OGM Tablo 2.18: Yanan alanların silvikültürel değerlendirmesi, 2024", "kurum": config["kaynaklar"]["ogm"]},
            {"ad": "OGM Tablo 2.15/2.16: Çıkış nedenlerinin ince kırılımı, 2024", "kurum": config["kaynaklar"]["ogm"]},
            {"ad": "OGM Tablo 2.12/2.13: Bölge müdürlüklerine göre yangın dağılımı, 2004-2024", "kurum": config["kaynaklar"]["ogm"]},
            {"ad": "OGM Tablo 2.17: Yangınların orman vasfına göre dağılımı, 2024", "kurum": config["kaynaklar"]["ogm"]},
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
            {"id": "orman_kaplama_korelasyonu.p_degeri", "tanim": "Pearson korelasyonunun anlamlılık testi (iki yönlü); p < 0,05 istatistiksel olarak anlamlı kabul edilir (α=0,05)", "birim": "0 ile 1 arası"},
            {"id": "kasit_orani_siralama.kasit_alan_oran / kasit_sayi_oran", "tanim": "Bölge müdürlüğü başına kasıt (kundaklama) kaynaklı yangınların payı, en az 15 yangınlık bölgeler arasında", "birim": "%"},
            {"id": "nedenler.egim.*_oran_egimi_puan_yil", "tanim": "Neden kategorisinin (kasıt/ihmal-kaza/doğal/bilinmeyen) yıllık payındaki doğrusal eğilim (basit doğrusal regresyon eğimi)", "birim": "yüzde puan/yıl"},
            {"id": "ulke_egimleri.egim_ha_yil", "tanim": "Ülkenin kendi yanan alan serisindeki doğrusal eğilim (basit doğrusal regresyon eğimi); pozitif değer artış, negatif değer azalış gösterir", "birim": "hektar/yıl"},
            {"id": "son_donem_karsilastirmasi.*", "tanim": "Son 10 yıl ile ondan önceki tüm dönemin (1988'e kadar) toplam/ortalama yanan alan ve yangın sayısı karşılaştırması", "birim": "hektar, adet, %"},
            {"id": "silvikultur_2024.*_oran", "tanim": "Yanan alanın, verilen işlem kategorisine (ağaçlandırma, gençleştirme, rehabilitasyon, gelecek yıllara bırakılan vb.) ayrılan payı", "birim": "%"},
            {"id": "nedenler.alt_kategori_2024", "tanim": "Çıkış nedeninin 14 alt-kategoriye (anız, sigara, piknik, kundaklama, terör, açma, enerji hattı, trafik kazası vb.) ayrıştırılmış hali, 2024", "birim": "hektar, adet"},
            {"id": "bolge_egim_2004_2024.egim_ha_yil", "tanim": "Bölge müdürlüğünün kendi yanan alan serisindeki (2004-2024) doğrusal eğilimi; pozitif değer artış, negatif değer azalış gösterir", "birim": "hektar/yıl"},
            {"id": "vasif_dagilimi_2024.*", "tanim": "Yanan alanın orman türüne (sağlıklı/verimli 'Normal Koru', bozuk 'Boşluklu Kapalı' olanlar, baltalık, makilik, ağaçlandırma sahası) göre dağılımı, 2024", "birim": "hektar, %"},
            {"id": "bolge_egim_kasit_korelasyonu.r_tum / r_haric", "tanim": "Bölgenin 2004-2024 yanan alan eğilimi ile 2025 kasıt oranı arasındaki Pearson korelasyonu; sırasıyla tüm veriyle ve iki uç nokta (Muğla, Antalya) çıkarılarak hesaplanmış", "birim": "-1 ile 1 arası"},
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
            "Ülke eğimleri (ulke_egimleri), her ülkenin kendi veri bulunan yıllarına göre hesaplandı; bazı ülkeler erken yıllarda EFFIS'e veri bildirmediği için ülkeler arasında kapsanan yıl sayısı farklı olabilir (en az 5 yıllık veri şartı arandı). Bu yüzden eğimler doğrudan aynı yıl aralığına göre birebir kıyaslanabilir değildir.",
            "Neden payı eğilimi (nedenler.egim) tek bir doğrusal eğim özetidir; yıldan yıla dalgalanmayı veya eğilimin yön değiştirdiği dönemleri yakalamaz. Sadece neden kırılımı yayınlanan yıllar (1997+) dahil edildi.",
            "Silvikültürel değerlendirme (Tablo 2.18) sadece 2024 için mevcut, çok yıllı seri yok; Milli Parklar bu tabloda ayrı sınıflandırıldığı için 30 bölge müdürlüğünü kapsıyor (bölge yangın tablosundaki 31'den farklı). OGM'nin kendi tablosunda Balıkesir satırının bileşen toplamı (261,41 ha) ile beyan edilen toplam alanı (260,86 ha) arasında ~0,55 ha'lık küçük bir yuvarlama farkı var. 'Gelecek yıllara bırakılan' kategorisi, o alanda hiçbir işlem yapılmayacağı anlamına gelmez — rapor tarihi itibarıyla henüz bir karara/uygulamaya geçilmediğini gösterir.",
            "Neden alt kategorisi kırılımı (Tablo 2.15/2.16) sadece 2024 için mevcut; 2025 Faaliyet Raporu bu düzeyde ayrıntı içermiyor. OGM'nin aynı yıllığındaki bu tablo ile ulusal 4-kategori tablosu arasında (aynı yıl için) birkaç yüzdelik küçük, bilinen bir tutarsızlık var — örn. kasıt toplamı bu tabloda 218,4 ha, ulusal tabloda 223 ha.",
            "Bölge müdürlüğü eğilimi (bolge_egim_2004_2024) 2004-2024 arası mevcut olan tek çok yıllı bölge serisidir; 2025 için bölge bazında sadece tek yıllık veri var (bolge_2025), bu yüzden 2025 bu eğilime dahil değil. En az 10 yıllık veri şartı arandı; tüm bölgeler zaten 21 yılın tamamını kapsıyor.",
            "Orman vasfına göre dağılım (Tablo 2.17) sadece 2024 için mevcut, çok yıllı seri yok.",
            "Bölge eğilimi ile kasıt oranı arasındaki korelasyon (bolge_egim_kasit_korelasyonu) örnek bir 'uç nokta etkisi' vakası: tüm veriyle r=0,83 (güçlü, anlamlı) ama Muğla ve Antalya çıkarıldığında r=-0,18'e (anlamsız) düşüyor — yani bu iki bölgeye özgü bir örtüşme, kasıtın kötüleşmeyi ulusal düzeyde açıkladığı iddia edilemez. İki farklı yıl (eğilim 2004-2024, kasıt oranı 2025) karşılaştırıldığı için nedensellik yönü de belirsizdir.",
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
