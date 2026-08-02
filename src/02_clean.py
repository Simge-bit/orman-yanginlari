"""data/interim/*_ham.csv dosyalarını okuyup il adlarını eşler, tipleri
dönüştürür, eksik değerleri işaretler ve tutarlılığı doğrular. Çıktı,
03_transform.py'nin girdisidir.
"""
import pandas as pd
from utils import data_path, standardize_il, load_config

SAYI_KOLONLARI_YILLIK = [
    "yanan_alan_ha", "yangin_sayisi",
    "kasit_sayi", "kasit_alan_ha",
    "ihmal_kaza_sayi", "ihmal_kaza_alan_ha",
    "dogal_sayi", "dogal_alan_ha",
    "bilinmeyen_sayi", "bilinmeyen_alan_ha",
]


def _sayiya_cevir(seri: pd.Series) -> pd.Series:
    # Excel'den gelen "-" eksik değeri, "2 411" gibi boşluklu binlik ayraçları temizler.
    temiz = seri.astype(str).str.replace(" ", "", regex=False).str.replace(" ", "", regex=False)
    temiz = temiz.replace({"-": None, "nan": None})
    return pd.to_numeric(temiz, errors="coerce")


def clean_yillik_seri():
    df = pd.read_csv(data_path("interim", "yillik_seri_ham.csv"))
    df["yil"] = df["yil"].astype(int)
    for kolon in SAYI_KOLONLARI_YILLIK:
        df[kolon] = _sayiya_cevir(df[kolon])

    # 1997 öncesi neden kırılımı OGM tablosunda hiç yayınlanmamış (NaN kalmalı, 0 değil).
    neden_var = df[["kasit_sayi", "ihmal_kaza_sayi", "dogal_sayi", "bilinmeyen_sayi"]].notna().all(axis=1)
    df["neden_kirilimi_var"] = neden_var

    toplam_sayi = df[["kasit_sayi", "ihmal_kaza_sayi", "dogal_sayi", "bilinmeyen_sayi"]].sum(axis=1)
    toplam_alan = df[["kasit_alan_ha", "ihmal_kaza_alan_ha", "dogal_alan_ha", "bilinmeyen_alan_ha"]].sum(axis=1)
    uyumsuz = neden_var & ((toplam_sayi != df["yangin_sayisi"]) | (toplam_alan.round(1) != df["yanan_alan_ha"].round(1)))
    if uyumsuz.any():
        print(f"[clean] UYARI: neden kırılımı toplamı yıl toplamıyla uyuşmuyor -> yıllar: {df.loc[uyumsuz, 'yil'].tolist()}")

    df.to_csv(data_path("interim", "yillik_seri.csv"), index=False)
    print(f"[clean] yillik_seri.csv: {len(df)} satır, neden kırılımı olan yıl sayısı: {neden_var.sum()}")


def clean_il_dagilim():
    df = pd.read_csv(data_path("interim", "il_dagilim_2025_ham.csv"))
    df["il"] = df["il"].apply(standardize_il)
    # Bu tabloda "-" (yillik_seri'deki neden kırılımının aksine) "veri yok"
    # değil "o il için 2025'te sıfır yangın/alan" anlamına geliyor — OGM
    # yayınladığı 81 ilin tamamı için bir satır veriyor, eksik il yok.
    df["yangin_sayisi"] = _sayiya_cevir(df["yangin_sayisi"]).fillna(0)
    df["yanan_alan_ha"] = _sayiya_cevir(df["yanan_alan_ha"]).fillna(0)

    if df["il"].duplicated().any():
        raise ValueError(f"Tekrarlanan il: {df.loc[df['il'].duplicated(), 'il'].tolist()}")
    if len(df) != 81:
        raise ValueError(f"81 il bekleniyordu, {len(df)} bulundu")

    df.to_csv(data_path("interim", "il_dagilim_2025.csv"), index=False)
    print(f"[clean] il_dagilim_2025.csv: {len(df)} il, toplam yangın={df['yangin_sayisi'].sum():.0f}, "
          f"toplam alan={df['yanan_alan_ha'].sum():.0f} ha")


def clean_orman_alani():
    df = pd.read_csv(data_path("interim", "orman_alani_il_ham.csv"))
    df["il"] = df["il"].apply(standardize_il)
    df["orman_alani_ha"] = _sayiya_cevir(df["orman_alani_ha"])
    df["orman_kaplama_yuzde"] = _sayiya_cevir(df["orman_kaplama_yuzde"])

    if len(df) != 81:
        raise ValueError(f"81 il bekleniyordu, {len(df)} bulundu")

    df.to_csv(data_path("interim", "orman_alani_il.csv"), index=False)
    print(f"[clean] orman_alani_il.csv: {len(df)} il")


def clean_effis():
    config = load_config()
    ulke_adi = {
        "TUR": "Türkiye", "GRC": "Yunanistan", "ESP": "İspanya",
        "ITA": "İtalya", "PRT": "Portekiz",
    }
    df = pd.read_csv(data_path("interim", "effis_ulke_ham.csv"))
    df["ulke"] = df["ulke_kodu"].map(ulke_adi)
    df["yanan_alan_ha"] = _sayiya_cevir(df["yanan_alan_ha"])
    df["yangin_sayisi"] = _sayiya_cevir(df["yangin_sayisi"])

    beklenen = set(config["karsilastirma_ulkeler"])
    eksik = beklenen - set(df["ulke"].dropna().unique())
    if eksik:
        print(f"[clean] UYARI: config.yaml'daki karşılaştırma ülkelerinden eksik: {eksik}")

    df = df.drop(columns=["ulke_kodu"])[["yil", "ulke", "yanan_alan_ha", "yangin_sayisi"]]
    df.to_csv(data_path("interim", "effis_ulke_karsilastirma.csv"), index=False)
    print(f"[clean] effis_ulke_karsilastirma.csv: {len(df)} satır, ülkeler: {sorted(df['ulke'].dropna().unique())}")


def clean_bolge_2025():
    df = pd.read_csv(data_path("interim", "bolge_yangin_2025_ham.csv"))
    df["yangin_sayisi"] = _sayiya_cevir(df["yangin_sayisi"])
    df["yanan_alan_ha"] = _sayiya_cevir(df["yanan_alan_ha"])

    yillik = pd.read_csv(data_path("interim", "yillik_seri.csv"))
    ulusal_2025 = yillik[yillik["yil"] == 2025].iloc[0]
    if df["yangin_sayisi"].sum() != ulusal_2025["yangin_sayisi"]:
        print(f"[clean] UYARI: bölge toplamı ({df['yangin_sayisi'].sum():.0f}) "
              f"ulusal 2025 toplamıyla ({ulusal_2025['yangin_sayisi']:.0f}) uyuşmuyor")
    if round(df["yanan_alan_ha"].sum(), 1) != round(ulusal_2025["yanan_alan_ha"], 1):
        print(f"[clean] UYARI: bölge alan toplamı ({df['yanan_alan_ha'].sum():.1f}) "
              f"ulusal 2025 toplamıyla ({ulusal_2025['yanan_alan_ha']:.1f}) uyuşmuyor")

    df.to_csv(data_path("interim", "bolge_yangin_2025.csv"), index=False)
    print(f"[clean] bolge_yangin_2025.csv: {len(df)} bölge müdürlüğü, "
          f"toplam yangın={df['yangin_sayisi'].sum():.0f}, toplam alan={df['yanan_alan_ha'].sum():.0f} ha")


def clean_bolge_neden_2025():
    df = pd.read_csv(data_path("interim", "bolge_neden_2025_ham.csv"))
    ham_kolonlar = [
        "ihmal_sayi", "ihmal_alan_ha", "kasit_sayi", "kasit_alan_ha",
        "kaza_sayi", "kaza_alan_ha", "bilinmeyen_sayi", "bilinmeyen_alan_ha",
        "yildirim_sayi", "yildirim_alan_ha",
    ]
    for kolon in ham_kolonlar:
        df[kolon] = _sayiya_cevir(df[kolon])

    # Ulusal tabloyla (4 kategori) tutarlı olsun diye İhmal+Kaza birleştirilir,
    # Yıldırım -> Doğal olarak yeniden adlandırılır (aynı şey, farklı isim).
    df["ihmal_kaza_sayi"] = df["ihmal_sayi"] + df["kaza_sayi"]
    df["ihmal_kaza_alan_ha"] = df["ihmal_alan_ha"] + df["kaza_alan_ha"]
    df["dogal_sayi"] = df["yildirim_sayi"]
    df["dogal_alan_ha"] = df["yildirim_alan_ha"]

    df["yangin_sayisi"] = df["kasit_sayi"] + df["ihmal_kaza_sayi"] + df["dogal_sayi"] + df["bilinmeyen_sayi"]
    df["yanan_alan_ha"] = df["kasit_alan_ha"] + df["ihmal_kaza_alan_ha"] + df["dogal_alan_ha"] + df["bilinmeyen_alan_ha"]

    for kategori in ["kasit", "ihmal_kaza", "dogal", "bilinmeyen"]:
        df[f"{kategori}_sayi_oran"] = df[f"{kategori}_sayi"] / df["yangin_sayisi"] * 100
        df[f"{kategori}_alan_oran"] = df[f"{kategori}_alan_ha"] / df["yanan_alan_ha"] * 100

    bolge_toplam = pd.read_csv(data_path("interim", "bolge_yangin_2025.csv"))
    kontrol = df[["bolge_muduru", "yangin_sayisi", "yanan_alan_ha"]].merge(
        bolge_toplam[["bolge_muduru", "yangin_sayisi", "yanan_alan_ha"]],
        on="bolge_muduru", suffixes=("_neden", "_toplam"),
    )
    # round() yerine mutlak fark: kayan nokta toplama hatası (ör. 3257.4500000000003)
    # yuvarlamada yanlışlıkla farklı yöne gidip yanlış alarm verebiliyor.
    uyumsuz = kontrol[
        (kontrol["yangin_sayisi_neden"] != kontrol["yangin_sayisi_toplam"])
        | ((kontrol["yanan_alan_ha_neden"] - kontrol["yanan_alan_ha_toplam"]).abs() > 0.1)
    ]
    if len(uyumsuz):
        print(f"[clean] UYARI: bölge neden kırılımı, bölge toplamıyla uyuşmuyor -> {uyumsuz['bolge_muduru'].tolist()}")

    kategoriler = ["kasit", "ihmal_kaza", "dogal", "bilinmeyen"]
    kolonlar = (
        ["bolge_muduru", "yangin_sayisi", "yanan_alan_ha"]
        + [f"{k}_{t}" for k in kategoriler for t in ("sayi", "alan_ha")]
        + [f"{k}_{t}_oran" for k in kategoriler for t in ("sayi", "alan")]
    )
    df[kolonlar].to_csv(data_path("interim", "bolge_neden_2025.csv"), index=False)
    print(f"[clean] bolge_neden_2025.csv: {len(df)} bölge müdürlüğü, neden oranları hesaplandı")


def clean_silvikultur_2025():
    df = pd.read_csv(data_path("interim", "silvikultur_2025_ham.csv"))
    bilesen_kolonlari = [
        "zarar_gormeyen_ha", "dogal_genclestirme_ha", "suni_genclestirme_ha",
        "rehabilitasyon_ha", "agaclandirma_ha", "koruma_ha", "gelecek_yillara_ha",
    ]
    # Bu tabloda "-" bir bölgede o kategoriye hiç alan düşmediği anlamına
    # gelir (il_dagilim'deki "sıfır yangın" kuralıyla aynı mantık) — 1997
    # öncesi ulusal seri gibi "henüz yayınlanmadı" değil, bu yüzden 0'a
    # çevriliyor (NaN olarak bırakılan yillik_seri'den farklı).
    for kolon in ["toplam_alan_ha"] + bilesen_kolonlari:
        df[kolon] = _sayiya_cevir(df[kolon]).fillna(0)

    bilesen_toplami = df[bilesen_kolonlari].sum(axis=1)
    uyumsuz = (bilesen_toplami - df["toplam_alan_ha"]).abs() > 0.5
    if uyumsuz.any():
        print(f"[clean] UYARI: silvikültür bileşenleri toplam alanla uyuşmuyor -> "
              f"{df.loc[uyumsuz, 'bolge_muduru'].tolist()}")

    ulusal = df[df["bolge_muduru"] == "Toplam-Total"].copy()
    bolge_df = df[df["bolge_muduru"] != "Toplam-Total"].copy()

    bolge_toplami = bolge_df["toplam_alan_ha"].sum()
    ulusal_alan = ulusal.iloc[0]["toplam_alan_ha"]
    if abs(bolge_toplami - ulusal_alan) > 1.0:
        print(f"[clean] UYARI: silvikültür bölge toplamı ({bolge_toplami:.1f}) "
              f"'Toplam-Total' satırıyla ({ulusal_alan:.1f}) uyuşmuyor")

    yillik = pd.read_csv(data_path("interim", "yillik_seri.csv"))
    ulusal_2025 = yillik[yillik["yil"] == 2025].iloc[0]
    if abs(ulusal_alan - ulusal_2025["yanan_alan_ha"]) > 1.0:
        print(f"[clean] UYARI: silvikültür ulusal toplamı ({ulusal_alan:.1f}) "
              f"2025 ulusal yangın toplamıyla ({ulusal_2025['yanan_alan_ha']:.1f}) uyuşmuyor")

    for kolon in bilesen_kolonlari:
        bolge_df[f"{kolon}_oran"] = bolge_df[kolon] / bolge_df["toplam_alan_ha"] * 100
        ulusal[f"{kolon}_oran"] = ulusal[kolon] / ulusal["toplam_alan_ha"] * 100

    bolge_df.to_csv(data_path("interim", "silvikultur_2025.csv"), index=False)
    ulusal.to_csv(data_path("interim", "silvikultur_2025_ulusal.csv"), index=False)
    print(f"[clean] silvikultur_2025.csv: {len(bolge_df)} bölge müdürlüğü, ulusal toplam {ulusal_alan:.0f} ha")


NEDEN_ALT_KATEGORILERI = [
    "ihmal_aniz", "ihmal_copluk", "ihmal_avcilik_coban",
    "ihmal_sigara", "ihmal_piknik", "ihmal_diger",
    "kasit_teror", "kasit_kundaklama", "kasit_acma", "kasit_diger",
    "kaza_enerji", "kaza_trafik", "kaza_diger",
    "bilinmeyen", "dogal",
]


def clean_neden_bolge_2025():
    alansal = pd.read_csv(data_path("interim", "neden_bolge_alansal_2025_ham.csv"))
    sayisal = pd.read_csv(data_path("interim", "neden_bolge_sayisal_2025_ham.csv"))

    for kolon in NEDEN_ALT_KATEGORILERI + ["toplam"]:
        alansal[kolon] = _sayiya_cevir(alansal[kolon]).fillna(0)
        sayisal[kolon] = _sayiya_cevir(sayisal[kolon]).fillna(0)

    alansal = alansal.rename(columns={k: f"{k}_ha" for k in NEDEN_ALT_KATEGORILERI + ["toplam"]})
    sayisal = sayisal.rename(columns={k: f"{k}_sayi" for k in NEDEN_ALT_KATEGORILERI + ["toplam"]})
    df = alansal.merge(sayisal, on="bolge_muduru", how="inner")

    alt_ha_kolonlari = [f"{k}_ha" for k in NEDEN_ALT_KATEGORILERI]
    alt_sayi_kolonlari = [f"{k}_sayi" for k in NEDEN_ALT_KATEGORILERI]
    fark_ha = (df[alt_ha_kolonlari].sum(axis=1) - df["toplam_ha"]).abs()
    fark_sayi = (df[alt_sayi_kolonlari].sum(axis=1) - df["toplam_sayi"]).abs()
    uyumsuz = (fark_ha > 1.0) | (fark_sayi > 1)
    if uyumsuz.any():
        print(f"[clean] UYARI: neden_bolge_2025 alt kategorileri toplamla uyuşmuyor -> "
              f"{df.loc[uyumsuz, 'bolge_muduru'].tolist()}")

    ulusal = df[df["bolge_muduru"] == "Toplam-Total"].copy()
    bolge_df = df[df["bolge_muduru"] != "Toplam-Total"].copy()

    bolge_toplam_ha = bolge_df["toplam_ha"].sum()
    ulusal_toplam_ha = ulusal.iloc[0]["toplam_ha"]
    if abs(bolge_toplam_ha - ulusal_toplam_ha) > 2.0:
        print(f"[clean] UYARI: neden_bolge_2025 bölge toplamı ({bolge_toplam_ha:.1f}) "
              f"'Toplam-Total' satırıyla ({ulusal_toplam_ha:.1f}) uyuşmuyor")

    # OGM'nin aynı yıllığındaki farklı tablolar (bu ince kırılım Tablo
    # 2.15/2.16 vs ulusal 4-kategori Tablo 2.x) arasında birkaç yüzdelik
    # küçük, bilinen bir tutarsızlık var (bkz. KAYNAKLAR.md) — burada
    # sadece bilgi amaçlı karşılaştırılıyor, hata olarak işlenmiyor.
    yillik = pd.read_csv(data_path("interim", "yillik_seri.csv"))
    ulusal_2025 = yillik[yillik["yil"] == 2025].iloc[0]
    fark_ulusal = abs(ulusal_toplam_ha - ulusal_2025["yanan_alan_ha"])
    print(f"[clean] neden_bolge_2025 ulusal toplam alan ({ulusal_toplam_ha:.1f} ha) ile "
          f"yillik_seri 2025 toplamı ({ulusal_2025['yanan_alan_ha']:.0f} ha) arasında fark: {fark_ulusal:.1f} ha")

    bolge_df.to_csv(data_path("interim", "neden_bolge_2025.csv"), index=False)
    ulusal.to_csv(data_path("interim", "neden_bolge_2025_ulusal.csv"), index=False)
    print(f"[clean] neden_bolge_2025.csv: {len(bolge_df)} bölge müdürlüğü")


def clean_bolge_cok_yillik():
    df = pd.read_csv(data_path("interim", "bolge_cok_yillik_ham.csv"))
    df["alan_ha"] = _sayiya_cevir(df["alan_ha"]).fillna(0)
    df["sayi"] = _sayiya_cevir(df["sayi"]).fillna(0)

    ulusal = df[df["bolge_muduru"] == "Toplam-Total"].copy()
    bolge_df = df[df["bolge_muduru"] != "Toplam-Total"].copy()

    # Her yıl için: 31 bölgenin (DKMPGM dahil) toplamı, o yılın kendi
    # "Toplam-Total" satırıyla eşleşmeli.
    bolge_yillik_toplam = bolge_df.groupby("yil")["alan_ha"].sum()
    ulusal_yillik = ulusal.set_index("yil")["alan_ha"]
    fark = (bolge_yillik_toplam - ulusal_yillik).abs()
    uyumsuz_yillar = fark[fark > 2.0].index.tolist()
    if uyumsuz_yillar:
        print(f"[clean] UYARI: bolge_cok_yillik bölge toplamı bazı yıllarda 'Toplam-Total' ile uyuşmuyor -> {uyumsuz_yillar}")

    # Örtüşen yıllarda (2004-2025) ulusal yillik_seri ile çapraz kontrol —
    # bilgi amaçlı, farklı OGM tabloları arasında küçük farklar bilinen bir durum.
    yillik_seri = pd.read_csv(data_path("interim", "yillik_seri.csv"))
    karsilastirma = ulusal.merge(yillik_seri[["yil", "yanan_alan_ha"]], on="yil", how="inner")
    fark_ulusal = (karsilastirma["alan_ha"] - karsilastirma["yanan_alan_ha"]).abs()
    uyumsuz_ulusal = karsilastirma.loc[fark_ulusal > 2.0, "yil"].tolist()
    if uyumsuz_ulusal:
        print(f"[clean] UYARI: bolge_cok_yillik ulusal toplamı yillik_seri ile bazı yıllarda uyuşmuyor -> {uyumsuz_ulusal}")

    bolge_df.to_csv(data_path("interim", "bolge_cok_yillik.csv"), index=False)
    print(f"[clean] bolge_cok_yillik.csv: {bolge_df['bolge_muduru'].nunique()} bölge, "
          f"{bolge_df['yil'].nunique()} yıl")


VASIF_KATEGORILERI = [
    "normal_koru_ha", "bosluklu_koru_ha", "normal_baltalik_ha",
    "bosluklu_baltalik_ha", "makilik_ha", "agaclandirma_sahasi_ha",
]


def clean_vasif_dagilimi_2025():
    df = pd.read_csv(data_path("interim", "vasif_dagilimi_2025_ham.csv"))
    for kolon in ["toplam_ha"] + VASIF_KATEGORILERI:
        df[kolon] = _sayiya_cevir(df[kolon]).fillna(0)

    bilesen_toplami = df[VASIF_KATEGORILERI].sum(axis=1)
    uyumsuz = (bilesen_toplami - df["toplam_ha"]).abs() > 1.0
    if uyumsuz.any():
        print(f"[clean] UYARI: vasıf kategorileri toplam alanla uyuşmuyor -> "
              f"{df.loc[uyumsuz, 'bolge_muduru'].tolist()}")

    ulusal = df[df["bolge_muduru"] == "Toplam-Total"].copy()
    bolge_df = df[df["bolge_muduru"] != "Toplam-Total"].copy()

    yillik = pd.read_csv(data_path("interim", "yillik_seri.csv"))
    ulusal_2025 = yillik[yillik["yil"] == 2025].iloc[0]
    ulusal_toplam = ulusal.iloc[0]["toplam_ha"]
    fark = abs(ulusal_toplam - ulusal_2025["yanan_alan_ha"])
    print(f"[clean] vasif_dagilimi_2025 ulusal toplam ({ulusal_toplam:.1f} ha) ile "
          f"yillik_seri 2025 toplamı ({ulusal_2025['yanan_alan_ha']:.0f} ha) arasında fark: {fark:.1f} ha")

    for kolon in VASIF_KATEGORILERI:
        ulusal[f"{kolon}_oran"] = ulusal[kolon] / ulusal["toplam_ha"] * 100
        bolge_df[f"{kolon}_oran"] = bolge_df[kolon] / bolge_df["toplam_ha"] * 100

    bolge_df.to_csv(data_path("interim", "vasif_dagilimi_2025.csv"), index=False)
    ulusal.to_csv(data_path("interim", "vasif_dagilimi_2025_ulusal.csv"), index=False)
    print(f"[clean] vasif_dagilimi_2025.csv: {len(bolge_df)} bölge müdürlüğü")


def main():
    clean_yillik_seri()
    clean_il_dagilim()
    clean_orman_alani()
    clean_effis()
    clean_bolge_2025()
    clean_bolge_neden_2025()
    clean_silvikultur_2025()
    clean_neden_bolge_2025()
    clean_bolge_cok_yillik()
    clean_vasif_dagilimi_2025()


if __name__ == "__main__":
    main()
