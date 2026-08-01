"""data/interim metriklerinden sıralamaları ve eğilimleri çıkarır:
il sıralaması, en kötü yıllar, uzun dönem eğim (artıyor mu?), ülkeler
arası Türkiye'nin konumu. Çıktılar 05_export.py'nin girdisidir.
"""
import numpy as np
import pandas as pd
from scipy import stats
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


def analyze_son_donem_karsilastirmasi():
    # En çarpıcı çerçeveleme: "son 10 yıl" ile "ondan önceki tüm dönemi"
    # karşılaştırmak. Yoğunlaşma analizi (en kötü 5 yıl) çarpıklığı
    # gösteriyor, ama bu ikili bölünme "yakın geçmiş, geride kalan onlarca
    # yıldan daha mı kötü" sorusuna tek bir net cevap veriyor.
    SON_KAC_YIL = 10
    df = pd.read_csv(data_path("interim", "yillik_metrikler.csv")).sort_values("yil")
    son_yil = int(df["yil"].max())
    sinir_yil = son_yil - SON_KAC_YIL + 1
    son_donem = df[df["yil"] >= sinir_yil]
    onceki_donem = df[df["yil"] < sinir_yil]
    toplam_alan = df["yanan_alan_ha"].sum()

    sonuc = pd.DataFrame([{
        "son_donem_kapsam": f"{sinir_yil}-{son_yil}",
        "son_donem_yil_sayisi": len(son_donem),
        "son_donem_toplam_alan_ha": round(float(son_donem["yanan_alan_ha"].sum()), 1),
        "son_donem_toplam_yangin_sayisi": int(son_donem["yangin_sayisi"].sum()),
        "son_donem_alan_orani_yuzde": round(float(son_donem["yanan_alan_ha"].sum() / toplam_alan * 100), 1),
        "onceki_donem_kapsam": f"{int(df['yil'].min())}-{sinir_yil - 1}",
        "onceki_donem_yil_sayisi": len(onceki_donem),
        "onceki_donem_toplam_alan_ha": round(float(onceki_donem["yanan_alan_ha"].sum()), 1),
        "onceki_donem_toplam_yangin_sayisi": int(onceki_donem["yangin_sayisi"].sum()),
        "ortalama_yillik_alan_kati": round(
            float(son_donem["yanan_alan_ha"].mean() / onceki_donem["yanan_alan_ha"].mean()), 2
        ),
    }])
    sonuc.to_csv(data_path("interim", "son_donem_karsilastirmasi.csv"), index=False)
    r = sonuc.iloc[0]
    print(f"[analyze] son_donem_karsilastirmasi.csv: son {SON_KAC_YIL} yıl ({r['son_donem_kapsam']}) "
          f"%{r['son_donem_alan_orani_yuzde']:.1f}'sini oluşturuyor, yıllık ortalama "
          f"{r['ortalama_yillik_alan_kati']:.1f} kat daha fazla")


def analyze_orman_kaplama_korelasyonu():
    # Daha ormanlık iller orantılı olarak daha mı çok yanıyor? il_metrikler
    # (yoğunluk indeksi) ile orman_alani_il (orman kaplama %) birleştirilip
    # Pearson korelasyonu VE anlamlılığı (p-değeri) hesaplanır — sadece r
    # katsayısı tek başına "ilişki yok/var" iddiası için yeterli değil.
    il_df = pd.read_csv(data_path("interim", "il_metrikler.csv"))
    orman_df = pd.read_csv(data_path("interim", "orman_alani_il.csv"))[["il", "orman_kaplama_yuzde"]]
    df = il_df.merge(orman_df, on="il", how="inner")

    r, p_degeri = stats.pearsonr(df["orman_kaplama_yuzde"], df["yogunluk_indeksi_yuzde"])
    sonuc = pd.DataFrame([{
        "iliski": "orman_kaplama_yuzde vs yogunluk_indeksi_yuzde",
        "pearson_r": round(float(r), 3),
        "p_degeri": round(float(p_degeri), 3),
        "anlamli_mi": bool(p_degeri < 0.05),
        "il_sayisi": len(df),
        "kapsam_yili": 2024,
    }])
    sonuc.to_csv(data_path("interim", "korelasyon.csv"), index=False)
    anlamli_metni = "anlamlı" if p_degeri < 0.05 else "anlamlı değil"
    print(f"[analyze] korelasyon.csv: orman kaplama %% ile yoğunluk indeksi arasında "
          f"r={r:.3f}, p={p_degeri:.3f} (istatistiksel olarak {anlamli_metni}, n={len(df)})")


def analyze_ulke_egimleri():
    # Türkiye'nin karşılaştırma grubundaki 5 ülke arasında SADECE anlık
    # sırası değil, zaman içindeki kendi eğilimi de merak ediliyor: yanan
    # alan azalıyor mu artıyor mu, ve bu diğer ülkelere göre nasıl?
    df = pd.read_csv(data_path("interim", "ulke_metrikler.csv"))
    satirlar = []
    for ulke, grup in df.groupby("ulke"):
        veri = grup.dropna(subset=["yanan_alan_ha"]).sort_values("yil")
        if len(veri) < 5:
            continue
        satirlar.append({
            "ulke": ulke,
            "kapsam": f"{int(veri['yil'].min())}-{int(veri['yil'].max())}",
            "veri_yil_sayisi": len(veri),
            "egim_ha_yil": _egim(veri["yil"], veri["yanan_alan_ha"]),
        })
    sonuc = pd.DataFrame(satirlar).sort_values("egim_ha_yil", ascending=False)
    sonuc.to_csv(data_path("interim", "ulke_egim.csv"), index=False)
    tr = sonuc[sonuc["ulke"] == "Türkiye"].iloc[0]
    print(f"[analyze] ulke_egim.csv: Türkiye'nin yıllık eğimi={tr['egim_ha_yil']:.1f} ha/yıl "
          f"({tr['kapsam']}); {len(sonuc)} ülke için hesaplandı")


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


def analyze_silvikultur_siralama():
    # Yanan alanın en büyük tek kalemi ulusal düzeyde "gelecek yıllara
    # bırakılan" (henüz hiçbir işlem yapılmamış) — hangi bölgelerde bu payın
    # orantısız yüksek olduğu, en az 50 ha'lık bölgeler arasında sıralanır
    # (çok küçük alanlı bir bölgede tek bir karar tüm oranı çarpıtmasın diye).
    MIN_ALAN_HA = 50
    df = pd.read_csv(data_path("interim", "silvikultur_2024.csv"))
    yeterli = df[df["toplam_alan_ha"] >= MIN_ALAN_HA].copy()
    yeterli["sira_gelecek_yillara_oran"] = yeterli["gelecek_yillara_ha_oran"].rank(ascending=False, method="min").astype(int)
    yeterli = yeterli.sort_values("sira_gelecek_yillara_oran")
    yeterli.to_csv(data_path("interim", "silvikultur_siralama_2024.csv"), index=False)
    ilk = yeterli.iloc[0]
    print(f"[analyze] silvikultur_siralama_2024.csv: en yüksek 'gelecek yıllara bırakılan' oranı="
          f"{ilk['bolge_muduru']} (%{ilk['gelecek_yillara_ha_oran']:.1f}, min {MIN_ALAN_HA} ha şartıyla)")


NEDEN_ALT_KATEGORILERI = [
    "ihmal_aniz", "ihmal_copluk", "ihmal_avcilik_coban",
    "ihmal_sigara", "ihmal_piknik", "ihmal_diger",
    "kasit_teror", "kasit_kundaklama", "kasit_acma", "kasit_diger",
    "kaza_enerji", "kaza_trafik", "kaza_diger",
    "bilinmeyen", "dogal",
]


def analyze_neden_alt_kategori_siralama():
    # Ulusal 4 kategorinin (kasıt/ihmal-kaza/doğal/bilinmeyen) altında,
    # gerçekte hangi TEK davranış en çok alanı yakıyor? 14 alt-nedeni alan
    # bazında sıralar.
    ulusal = pd.read_csv(data_path("interim", "neden_bolge_2024_ulusal.csv")).iloc[0]
    satirlar = [{
        "kategori": kategori,
        "alan_ha": float(ulusal[f"{kategori}_ha"]),
        "sayi": float(ulusal[f"{kategori}_sayi"]),
    } for kategori in NEDEN_ALT_KATEGORILERI]
    sonuc = pd.DataFrame(satirlar).sort_values("alan_ha", ascending=False)
    sonuc.to_csv(data_path("interim", "neden_alt_kategori_siralama_2024.csv"), index=False)
    ilk = sonuc.iloc[0]
    print(f"[analyze] neden_alt_kategori_siralama_2024.csv: en büyük tek alt-neden="
          f"{ilk['kategori']} ({ilk['alan_ha']:.0f} ha)")


def analyze_bolge_cok_yillik_egim():
    # Bölge verisinin sadece 2025'te tek yıl var sanılıyordu — bu tablo
    # (2004-2024) aslında 21 yıllık bir seri, yani ülke karşılaştırmasında
    # yaptığımız "kendi eğilimi" analizinin bölge müdürlüğü versiyonu
    # mümkün: hangi bölge gerçekten kötüleşti, hangisi iyileşti?
    MIN_VERI_YILI = 10
    df = pd.read_csv(data_path("interim", "bolge_cok_yillik.csv"))
    satirlar = []
    for bolge, grup in df.groupby("bolge_muduru"):
        grup = grup.sort_values("yil")
        if len(grup) < MIN_VERI_YILI:
            continue
        satirlar.append({
            "bolge_muduru": bolge,
            "kapsam": f"{int(grup['yil'].min())}-{int(grup['yil'].max())}",
            "veri_yil_sayisi": len(grup),
            "egim_ha_yil": _egim(grup["yil"], grup["alan_ha"]),
            "toplam_ha": float(grup["alan_ha"].sum()),
            "ortalama_yillik_ha": float(grup["alan_ha"].mean()),
        })
    sonuc = pd.DataFrame(satirlar).sort_values("egim_ha_yil", ascending=False)
    sonuc.to_csv(data_path("interim", "bolge_cok_yillik_egim.csv"), index=False)
    en_kotu = sonuc.iloc[0]
    en_iyi = sonuc.iloc[-1]
    print(f"[analyze] bolge_cok_yillik_egim.csv: en hızlı kötüleşen={en_kotu['bolge_muduru']} "
          f"({en_kotu['egim_ha_yil']:+.1f} ha/yıl), en hızlı iyileşen={en_iyi['bolge_muduru']} "
          f"({en_iyi['egim_ha_yil']:+.1f} ha/yıl)")


def analyze_vasif_siralama():
    # Yanan alan sağlıklı/verimli orman mı ("Normal Koru"), yoksa bozuk/
    # bakımsız mı ("Boşluklu Kapalı" olanlar)? Ulusal düzeyde kategori
    # payları hesaplanır.
    ulusal = pd.read_csv(data_path("interim", "vasif_dagilimi_2024_ulusal.csv")).iloc[0]
    kategoriler = [
        "normal_koru_ha", "bosluklu_koru_ha", "normal_baltalik_ha",
        "bosluklu_baltalik_ha", "makilik_ha", "agaclandirma_sahasi_ha",
    ]
    satirlar = [{
        "kategori": kategori,
        "alan_ha": float(ulusal[kategori]),
        "oran_yuzde": float(ulusal[f"{kategori}_oran"]),
    } for kategori in kategoriler]
    sonuc = pd.DataFrame(satirlar).sort_values("alan_ha", ascending=False)
    sonuc.to_csv(data_path("interim", "vasif_siralama_2024.csv"), index=False)
    ilk = sonuc.iloc[0]
    print(f"[analyze] vasif_siralama_2024.csv: en büyük kategori={ilk['kategori']} "
          f"(%{ilk['oran_yuzde']:.1f})")


def analyze_bolge_egim_kasit_korelasyonu():
    # En güçlü tekil korelasyon bulgusu burada çıktı (r≈0.83) ama dikkatli
    # sunulmalı: bu kadar yüksek bir katsayı, aslında sadece iki uç
    # noktadan (Muğla, Antalya — hem en hızlı kötüleşen hem en yüksek
    # kasıt oranına sahip bölgeler) kaynaklanıyor olabilir. Bu iki bölge
    # çıkarıldığında ilişkinin tamamen kaybolup kaybolmadığını da
    # hesaplayıp birlikte raporluyoruz — yoksa "kasıt, kötüleşmeyi ulusal
    # düzeyde açıklıyor" gibi yanıltıcı bir genelleme çıkarılabilir.
    UC_NOKTALAR = ["Muğla", "Antalya"]
    egim = pd.read_csv(data_path("interim", "bolge_cok_yillik_egim.csv"))
    # kasıt oranı sıralaması zaten en az 15 yangınlık bölgelerle sınırlı
    # (bkz. analyze_bolge_neden_siralama) — küçük örneklemde oranın
    # tesadüfen çarpık çıkmasını önlemek için aynı eşik burada da kullanılıyor.
    kasit = pd.read_csv(data_path("interim", "bolge_neden_siralama_2025.csv"))
    df = egim.merge(kasit[["bolge_muduru", "kasit_alan_oran", "yangin_sayisi"]], on="bolge_muduru", how="inner")

    r_tum, p_tum = stats.pearsonr(df["egim_ha_yil"], df["kasit_alan_oran"])
    haric = df[~df["bolge_muduru"].isin(UC_NOKTALAR)]
    r_haric, p_haric = stats.pearsonr(haric["egim_ha_yil"], haric["kasit_alan_oran"])

    ozet = pd.DataFrame([{
        "n_tum": len(df), "r_tum": r_tum, "p_tum": p_tum,
        "n_haric": len(haric), "r_haric": r_haric, "p_haric": p_haric,
        "uc_noktalar": ", ".join(UC_NOKTALAR),
    }])
    ozet.to_csv(data_path("interim", "bolge_egim_kasit_korelasyonu.csv"), index=False)
    df.to_csv(data_path("interim", "bolge_egim_kasit_veri.csv"), index=False)
    print(f"[analyze] bolge_egim_kasit_korelasyonu.csv: tüm veri r={r_tum:.3f} (p={p_tum:.4f}, n={len(df)}), "
          f"{'/'.join(UC_NOKTALAR)} hariç r={r_haric:.3f} (p={p_haric:.4f}, n={len(haric)})")


def main():
    analyze_il_siralama()
    analyze_yillik_siralama_ve_egim()
    analyze_ulke_konumu()
    analyze_bolge_2025()
    analyze_bolge_neden_siralama()
    analyze_yogunlasma()
    analyze_son_donem_karsilastirmasi()
    analyze_orman_kaplama_korelasyonu()
    analyze_neden_egimi()
    analyze_ulke_egimleri()
    analyze_silvikultur_siralama()
    analyze_neden_alt_kategori_siralama()
    analyze_bolge_cok_yillik_egim()
    analyze_bolge_egim_kasit_korelasyonu()
    analyze_vasif_siralama()


if __name__ == "__main__":
    main()
