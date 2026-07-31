"""Temizlenmiş data/interim tablolarından türetilmiş metrikleri hesaplar:
ortalama büyüklük, hareketli ortalama, yoğunluk indeksi, neden oranları,
ülke payları. Çıktılar 04_analyze.py'nin girdisidir.
"""
import pandas as pd
from utils import data_path, load_config

NEDEN_KATEGORILERI = ["kasit", "ihmal_kaza", "dogal", "bilinmeyen"]


def transform_yillik_metrikler(config: dict):
    df = pd.read_csv(data_path("interim", "yillik_seri.csv")).sort_values("yil")

    df["ortalama_buyukluk_ha"] = df["yanan_alan_ha"] / df["yangin_sayisi"]

    pencere = config["hareketli_ort_penceresi"]
    df["ma_yangin_sayisi"] = df["yangin_sayisi"].rolling(pencere, min_periods=1).mean()
    df["ma_yanan_alan_ha"] = df["yanan_alan_ha"].rolling(pencere, min_periods=1).mean()

    for kategori in NEDEN_KATEGORILERI:
        sayi_col, alan_col = f"{kategori}_sayi", f"{kategori}_alan_ha"
        df[f"{kategori}_sayi_oran"] = (df[sayi_col] / df["yangin_sayisi"] * 100).where(df["neden_kirilimi_var"])
        df[f"{kategori}_alan_oran"] = (df[alan_col] / df["yanan_alan_ha"] * 100).where(df["neden_kirilimi_var"])

    df.to_csv(data_path("interim", "yillik_metrikler.csv"), index=False)
    print(f"[transform] yillik_metrikler.csv: {len(df)} satır, "
          f"hareketli ortalama penceresi={pencere} yıl")

    print("[transform] NOT: aylık/mevsimsel kırılım OGM'nin yıllık istatistik "
          "yayınında yok — mevsimsellik metriği hesaplanamadı, ayrı bir aylık "
          "kaynak bulunursa eklenebilir.")
    print("[transform] NOT: 'mega yangın' eşiği (config: "
          f"{config['esikler']['mega_yangin_ha']} ha) tekil yangın kaydı "
          "gerektirir; elimizdeki veri yıllık/il toplamları düzeyinde olduğu "
          "için bu eşik uygulanamadı.")


def transform_il_metrikleri():
    il_df = pd.read_csv(data_path("interim", "il_dagilim_2024.csv"))
    orman_df = pd.read_csv(data_path("interim", "orman_alani_il.csv"))[["il", "orman_alani_ha"]]

    df = il_df.merge(orman_df, on="il", how="left", validate="one_to_one")
    if df["orman_alani_ha"].isna().any():
        raise ValueError(f"Orman alanı eşleşmeyen il: {df.loc[df['orman_alani_ha'].isna(), 'il'].tolist()}")

    df["ortalama_buyukluk_ha"] = df["yanan_alan_ha"] / df["yangin_sayisi"].replace(0, pd.NA)
    df["yogunluk_indeksi_yuzde"] = df["yanan_alan_ha"] / df["orman_alani_ha"] * 100

    df.to_csv(data_path("interim", "il_metrikler.csv"), index=False)
    print(f"[transform] il_metrikler.csv: {len(df)} il, yoğunluk indeksi = "
          "yanan alan / toplam orman alanı (%)")


def transform_ulke_metrikleri():
    df = pd.read_csv(data_path("interim", "effis_ulke_karsilastirma.csv")).sort_values(["yil", "ulke"])

    df["ortalama_buyukluk_ha"] = df["yanan_alan_ha"] / df["yangin_sayisi"]

    yillik_toplam = df.groupby("yil")["yanan_alan_ha"].transform("sum")
    df["alan_payi_yuzde"] = df["yanan_alan_ha"] / yillik_toplam * 100

    df.to_csv(data_path("interim", "ulke_metrikler.csv"), index=False)
    print(f"[transform] ulke_metrikler.csv: {len(df)} satır — 'alan_payi_yuzde' "
          "o yıl karşılaştırma grubundaki (5 ülke) toplam yanan alan içindeki payı gösterir")


def main():
    config = load_config()
    transform_yillik_metrikler(config)
    transform_il_metrikleri()
    transform_ulke_metrikleri()


if __name__ == "__main__":
    main()
