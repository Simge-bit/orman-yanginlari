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
    df = pd.read_csv(data_path("interim", "il_dagilim_2024_ham.csv"))
    df["il"] = df["il"].apply(standardize_il)
    # Bu tabloda "-" (yillik_seri'deki neden kırılımının aksine) "veri yok"
    # değil "o il için 2024'te sıfır yangın/alan" anlamına geliyor — OGM
    # yayınladığı 81 ilin tamamı için bir satır veriyor, eksik il yok.
    df["yangin_sayisi"] = _sayiya_cevir(df["yangin_sayisi"]).fillna(0)
    df["yanan_alan_ha"] = _sayiya_cevir(df["yanan_alan_ha"]).fillna(0)

    if df["il"].duplicated().any():
        raise ValueError(f"Tekrarlanan il: {df.loc[df['il'].duplicated(), 'il'].tolist()}")
    if len(df) != 81:
        raise ValueError(f"81 il bekleniyordu, {len(df)} bulundu")

    df.to_csv(data_path("interim", "il_dagilim_2024.csv"), index=False)
    print(f"[clean] il_dagilim_2024.csv: {len(df)} il, toplam yangın={df['yangin_sayisi'].sum():.0f}, "
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


def main():
    clean_yillik_seri()
    clean_il_dagilim()
    clean_orman_alani()
    clean_effis()
    clean_bolge_2025()
    clean_bolge_neden_2025()


if __name__ == "__main__":
    main()
