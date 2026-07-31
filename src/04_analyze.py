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


def analyze_bolge_neden_siralama():
    # En çok merak edilen soru: hangi bölgede kasıt (kundaklama) payı orantısız
    # yüksek? En az 15 yangınlık bölgeler dahil edilir — Sinop (18) gibi çok
    # az sayıda yangınla oranın tesadüfen çarpık çıkmasını önlemek için.
    MIN_YANGIN = 15
    df = pd.read_csv(data_path("interim", "bolge_neden_2025.csv"))
    yeterli = df[df["yangin_sayisi"] >= MIN_YANGIN].copy()
    yeterli["sira_kasit_alan_oran"] = yeterli["kasit_alan_oran"].rank(ascending=False, method="min").astype(int)
    yeterli["sira_kasit_sayi_oran"] = yeterli["kasit_sayi_oran"].rank(ascending=False, method="min").astype(int)
    yeterli = yeterli.sort_values("sira_kasit_alan_oran")
    yeterli.to_csv(data_path("interim", "bolge_neden_siralama_2025.csv"), index=False)
    ilk = yeterli.iloc[0]
    print(f"[analyze] bolge_neden_siralama_2025.csv: en yüksek kasıt (alan) oranı="
          f"{ilk['bolge_muduru']} (%{ilk['kasit_alan_oran']:.1f}, min {MIN_YANGIN} yangın şartıyla)")


def analyze_yogunlasma():
    # "Kaç kötü yıl toplamın büyük kısmını oluşturuyor?" — yıldan yıla
    # ortalamaya bakmanın gizlediği bir çarpıklık/yoğunlaşma ölçüsü.
    EN_KOTU_YIL_SAYISI = 5
    df = pd.read_csv(data_path("interim", "yillik_metrikler.csv")).sort_values("yil")
    toplam_ha = df["yanan_alan_ha"].sum()
    en_kotu = df.nlargest(EN_KOTU_YIL_SAYISI, "yanan_alan_ha")
    en_kotu_toplam = en_kotu["yanan_alan_ha"].sum()
    sonuc = pd.DataFrame([{
        "toplam_yil_sayisi": len(df),
        "en_kotu_yil_sayisi": EN_KOTU_YIL_SAYISI,
        "en_kotu_yillar_toplam_ha": round(en_kotu_toplam, 1),
        "genel_toplam_ha": round(toplam_ha, 1),
        "en_kotu_yillar_orani_yuzde": round(en_kotu_toplam / toplam_ha * 100, 1),
        "en_kotu_yillar": ", ".join(str(y) for y in sorted(en_kotu["yil"])),
    }])
    sonuc.to_csv(data_path("interim", "yogunlasma.csv"), index=False)
    print(f"[analyze] yogunlasma.csv: en kötü {EN_KOTU_YIL_SAYISI} yıl ({sonuc.iloc[0]['en_kotu_yillar']}), "
          f"{len(df)} yıllık toplamın %{sonuc.iloc[0]['en_kotu_yillar_orani_yuzde']:.1f}'ini oluşturuyor")


def analyze_orman_kaplama_korelasyonu():
    # Daha ormanlık iller orantılı olarak daha mı çok yanıyor? il_metrikler
    # (yoğunluk indeksi) ile orman_alani_il (orman kaplama %) birleştirilip
    # Pearson korelasyonu hesaplanır.
    il_df = pd.read_csv(data_path("interim", "il_metrikler.csv"))
    orman_df = pd.read_csv(data_path("interim", "orman_alani_il.csv"))[["il", "orman_kaplama_yuzde"]]
    df = il_df.merge(orman_df, on="il", how="inner")

    r = df["orman_kaplama_yuzde"].corr(df["yogunluk_indeksi_yuzde"])
    sonuc = pd.DataFrame([{
        "iliski": "orman_kaplama_yuzde vs yogunluk_indeksi_yuzde",
        "pearson_r": round(float(r), 3),
        "il_sayisi": len(df),
        "kapsam_yili": 2024,
    }])
    sonuc.to_csv(data_path("interim", "korelasyon.csv"), index=False)
    print(f"[analyze] korelasyon.csv: orman kaplama %% ile yoğunluk indeksi arasında r={r:.3f} (n={len(df)})")


def analyze_neden_egimi():
    # "Kasıt artıyor mu, ihmal-kaza azalıyor mu?" — her nedenin yıllık
    # payının (sayı ve alan bazında) doğrusal eğilimi. Sadece neden
    # kırılımı yayınlanan yıllarda (1997+) hesaplanır.
    df = pd.read_csv(data_path("interim", "yillik_metrikler.csv")).sort_values("yil")
    df = df[df["neden_kirilimi_var"]]
    kapsam = f"{int(df['yil'].min())}-{int(df['yil'].max())}"
    kategoriler = ["kasit", "ihmal_kaza", "dogal", "bilinmeyen"]
    satirlar = [{
        "kapsam": kapsam,
        "kategori": kategori,
        "sayi_oran_egimi_puan_yil": _egim(df["yil"], df[f"{kategori}_sayi_oran"]),
        "alan_oran_egimi_puan_yil": _egim(df["yil"], df[f"{kategori}_alan_oran"]),
    } for kategori in kategoriler]
    sonuc = pd.DataFrame(satirlar)
    sonuc.to_csv(data_path("interim", "neden_egimi.csv"), index=False)
    kasit = sonuc[sonuc["kategori"] == "kasit"].iloc[0]
    print(f"[analyze] neden_egimi.csv ({kapsam}): kasıt payı (alan) yılda "
          f"{kasit['alan_oran_egimi_puan_yil']:+.2f} puan değişiyor")


def main():
    analyze_il_siralama()
    analyze_yillik_siralama_ve_egim()
    analyze_ulke_konumu()
    analyze_bolge_2025()
    analyze_bolge_neden_siralama()
    analyze_yogunlasma()
    analyze_orman_kaplama_korelasyonu()
    analyze_neden_egimi()


if __name__ == "__main__":
    main()
