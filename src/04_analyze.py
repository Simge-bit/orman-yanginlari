"""data/interim metriklerinden sıralamaları ve eğilimleri çıkarır:
il sıralaması, en kötü yıllar, uzun dönem eğim (artıyor mu?), ülkeler
arası Türkiye'nin konumu. Çıktılar 05_export.py'nin girdisidir.
"""
import numpy as np
import pandas as pd
from utils import data_path


def analyze_il_siralama():
    df = pd.read_csv(data_path("interim", "il_metrikler.csv"))
    df["sira_alan"] = df["yanan_alan_ha"].rank(ascending=False, method="min").astype(int)
    df["sira_yogunluk"] = df["yogunluk_indeksi_yuzde"].rank(ascending=False, method="min").astype(int)
    df = df.sort_values("sira_alan")
    df.to_csv(data_path("interim", "il_siralama.csv"), index=False)
    print(f"[analyze] il_siralama.csv: en çok yanan il={df.iloc[0]['il']} "
          f"({df.iloc[0]['yanan_alan_ha']:.0f} ha)")


def _egim(yil: pd.Series, deger: pd.Series) -> float:
    egim, _ = np.polyfit(yil, deger, 1)
    return egim


def analyze_yillik_siralama_ve_egim():
    df = pd.read_csv(data_path("interim", "yillik_metrikler.csv")).sort_values("yil")
    df["sira_alan"] = df["yanan_alan_ha"].rank(ascending=False, method="min").astype(int)
    df["sira_sayi"] = df["yangin_sayisi"].rank(ascending=False, method="min").astype(int)
    df.sort_values("sira_alan").to_csv(data_path("interim", "yillik_siralama.csv"), index=False)

    tum_donem = {
        "kapsam": f"{int(df['yil'].min())}-{int(df['yil'].max())}",
        "alan_egimi_ha_yil": _egim(df["yil"], df["yanan_alan_ha"]),
        "sayi_egimi_adet_yil": _egim(df["yil"], df["yangin_sayisi"]),
        "ortalama_buyukluk_egimi_ha_yil": _egim(df["yil"], df["ortalama_buyukluk_ha"]),
    }
    son_10 = df[df["yil"] >= df["yil"].max() - 9]
    son_10_yil = {
        "kapsam": f"{int(son_10['yil'].min())}-{int(son_10['yil'].max())}",
        "alan_egimi_ha_yil": _egim(son_10["yil"], son_10["yanan_alan_ha"]),
        "sayi_egimi_adet_yil": _egim(son_10["yil"], son_10["yangin_sayisi"]),
        "ortalama_buyukluk_egimi_ha_yil": _egim(son_10["yil"], son_10["ortalama_buyukluk_ha"]),
    }
    egim_df = pd.DataFrame([tum_donem, son_10_yil])
    egim_df.to_csv(data_path("interim", "yillik_egim.csv"), index=False)
    print(f"[analyze] yillik_siralama.csv: en büyük yıl={int(df.loc[df['sira_alan']==1,'yil'].iloc[0])}")
    print(f"[analyze] yillik_egim.csv: tüm dönem alan eğimi={tum_donem['alan_egimi_ha_yil']:.1f} ha/yıl, "
          f"son 10 yıl={son_10_yil['alan_egimi_ha_yil']:.1f} ha/yıl")


def analyze_ulke_konumu():
    df = pd.read_csv(data_path("interim", "ulke_metrikler.csv"))
    # Bazı ülkeler erken yıllarda EFFIS'e veri bildirmemiş (NaN) — nullable
    # Int64 kullanılıyor ki bu yıllar sıralamadan düşsün, hataya yol açmasın.
    df["sira_alan"] = df.groupby("yil")["yanan_alan_ha"].rank(ascending=False, method="min").astype("Int64")
    df.to_csv(data_path("interim", "ulke_siralama.csv"), index=False)

    tr = df[df["ulke"] == "Türkiye"]
    ortalama_sira = tr["sira_alan"].mean()
    print(f"[analyze] ulke_siralama.csv: Türkiye'nin 5 ülke arasında ortalama sırası (alan)={ortalama_sira:.1f}")


def analyze_bolge_2025():
    df = pd.read_csv(data_path("interim", "bolge_yangin_2025.csv"))
    df["sira_alan"] = df["yanan_alan_ha"].rank(ascending=False, method="min").astype(int)
    df = df.sort_values("sira_alan")
    df.to_csv(data_path("interim", "bolge_siralama_2025.csv"), index=False)
    print(f"[analyze] bolge_siralama_2025.csv: en çok yanan bölge müdürlüğü={df.iloc[0]['bolge_muduru']} "
          f"({df.iloc[0]['yanan_alan_ha']:.0f} ha)")


def main():
    analyze_il_siralama()
    analyze_yillik_siralama_ve_egim()
    analyze_ulke_konumu()
    analyze_bolge_2025()


if __name__ == "__main__":
    main()
