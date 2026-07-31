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
    df["yangin_sayisi"] = _sayiya_cevir(df["yangin_sayisi"])
    df["yanan_alan_ha"] = _sayiya_cevir(df["yanan_alan_ha"])

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


def main():
    clean_yillik_seri()
    clean_il_dagilim()
    clean_orman_alani()
    clean_effis()


if __name__ == "__main__":
    main()
