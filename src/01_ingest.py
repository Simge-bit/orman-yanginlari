"""Ham OGM/EFFIS Excel dosyalarındaki çok satırlı başlıkları ayıklayıp
data/interim/ altına düz (tidy) ama henüz temizlenmemiş tablolar yazar.
İş mantığı (il eşleme, tip dönüşümü, doğrulama) 02_clean.py'de yapılır.
"""
import pandas as pd
from utils import data_path


def ingest_yillik_seri():
    df = pd.read_excel(data_path("raw", "ogm_yillik_yangin_1988_2024.xls"), header=None)
    rows = df.iloc[8:45]
    out = pd.DataFrame({
        "yil": rows[0],
        "yanan_alan_ha": rows[1],
        "yangin_sayisi": rows[3],
        "kasit_sayi": rows[5],
        "kasit_alan_ha": rows[6],
        "ihmal_kaza_sayi": rows[8],
        "ihmal_kaza_alan_ha": rows[9],
        "dogal_sayi": rows[11],
        "dogal_alan_ha": rows[12],
        "bilinmeyen_sayi": rows[14],
        "bilinmeyen_alan_ha": rows[15],
    })

    # 2025: "Ormancılık İstatistikleri" yıllığının henüz 2025 sürümü yok
    # (erişim: 2026-07-31) — OGM'nin kendi 2025 Faaliyet Raporu'ndan (Tablo
    # 16/17) resmi ama ayrı bir yayın olarak ekleniyor. Bkz. KAYNAKLAR.md.
    ek_2025 = pd.read_csv(data_path("raw", "ogm_faaliyet_raporu_2025_yangin.csv"))
    out = pd.concat([out, ek_2025], ignore_index=True)

    out.to_csv(data_path("interim", "yillik_seri_ham.csv"), index=False)
    print(f"[ingest] yillik_seri_ham.csv: {len(out)} satır (1988-2025)")


def ingest_il_dagilim():
    df = pd.read_excel(data_path("raw", "ogm_il_yangin_dagilimi_2024.xlsx"), header=None)
    sol = df.iloc[4:44][[0, 1, 2, 3]]
    sag = df.iloc[3:44][[5, 6, 7, 8]]
    sol.columns = sag.columns = ["ibbs_kodu", "il", "yangin_sayisi", "yanan_alan_ha"]
    out = pd.concat([sol, sag], ignore_index=True).dropna(subset=["il"])
    out.to_csv(data_path("interim", "il_dagilim_2024_ham.csv"), index=False)
    print(f"[ingest] il_dagilim_2024_ham.csv: {len(out)} satır (beklenen: 81)")


def ingest_orman_alani():
    df = pd.read_excel(data_path("raw", "ref_orman_alani_il_2024.xlsx"), header=None)
    rows = df.iloc[6:87]
    out = pd.DataFrame({
        "ibbs_kodu": rows[0],
        "il": rows[1],
        "orman_alani_ha": rows[5],
        "orman_kaplama_yuzde": rows[6],
    })
    out.to_csv(data_path("interim", "orman_alani_il_ham.csv"), index=False)
    print(f"[ingest] orman_alani_il_ham.csv: {len(out)} satır (beklenen: 81)")


def ingest_effis():
    xls = pd.ExcelFile(data_path("raw", "effis_ulke_karsilastirma_1980_2024.xlsx"))
    ulke_kodlari = ["TUR", "GRC", "ESP", "ITA", "PRT"]
    frames = []
    for sheet, metrik in [
        ("Burnt area (ha) 1980 - 204", "yanan_alan_ha"),
        ("Nr. of forest fires 1980 - 2024", "yangin_sayisi"),
    ]:
        df = pd.read_excel(xls, sheet_name=sheet, header=0)
        df = df.rename(columns={"Year": "yil"})[["yil"] + ulke_kodlari]
        long = df.melt(id_vars="yil", var_name="ulke_kodu", value_name=metrik)
        frames.append(long.set_index(["yil", "ulke_kodu"]))
    out = pd.concat(frames, axis=1).reset_index()
    out.to_csv(data_path("interim", "effis_ulke_ham.csv"), index=False)
    print(f"[ingest] effis_ulke_ham.csv: {len(out)} satır")


def ingest_bolge_2025():
    # İl bazında 2025 verisi hiçbir resmi kaynakta yok (bkz. KAYNAKLAR.md) —
    # bu, aynı Faaliyet Raporu'nun "Orman Bölge Müdürlükleri" (~30 bölge,
    # il değil) düzeyindeki tek 2025 coğrafi kırılımı. Zaten temiz bir CSV,
    # sadece geçiyor.
    df = pd.read_csv(data_path("raw", "ogm_faaliyet_raporu_2025_bolge_yangin.csv"))
    df.to_csv(data_path("interim", "bolge_yangin_2025_ham.csv"), index=False)
    print(f"[ingest] bolge_yangin_2025_ham.csv: {len(df)} bölge müdürlüğü")


def ingest_bolge_neden_2025():
    # Aynı Faaliyet Raporu Ek 6 tablosunun neden kırılımı — bölge müdürlüğü
    # başına İhmal/Kasıt/Kaza/Bilinmeyen/Yıldırım (5 kategori, ulusal
    # tablonun 4 kategorisinden daha ince: İhmal ve Kaza burada ayrı).
    # PDF'ten çıkarılırken her satır kendi TOPLAM'ı ve
    # ogm_faaliyet_raporu_2025_bolge_yangin.csv ile program dışında
    # (scratchpad/bolge_neden_dogrula.py) çapraz doğrulandı, 0 hata.
    df = pd.read_csv(data_path("raw", "ogm_faaliyet_raporu_2025_bolge_neden.csv"))
    df.to_csv(data_path("interim", "bolge_neden_2025_ham.csv"), index=False)
    print(f"[ingest] bolge_neden_2025_ham.csv: {len(df)} bölge müdürlüğü")


def ingest_silvikultur_2024():
    # OGM Tablo 2.18: 2024'te yanan alana ne olduğu (ağaçlandırma programına
    # mı alındı, gençleştirildi mi, yoksa "gelecek yıllara" mı bırakıldı) —
    # bölge müdürlüğü bazında. "Toplam-Total" satırı ulusal toplamı, geri
    # kalan 30 satır bölgeleri veriyor (Milli Parklar bu tabloda ayrı
    # sınıflandırılmış, dahil değil — bkz. KAYNAKLAR.md).
    df = pd.read_excel(
        data_path("raw", "ogm_silvikultur_degerlendirme_2024.xlsx"),
        sheet_name="2.18",
        skiprows=3,
        header=None,
        usecols=range(9),
        names=[
            "bolge_muduru", "toplam_alan_ha", "zarar_gormeyen_ha",
            "dogal_genclestirme_ha", "suni_genclestirme_ha", "rehabilitasyon_ha",
            "agaclandirma_ha", "koruma_ha", "gelecek_yillara_ha",
        ],
    )
    df = df.dropna(subset=["bolge_muduru"])
    df = df[~df["bolge_muduru"].astype(str).str.startswith("Not")]
    df.to_csv(data_path("interim", "silvikultur_2024_ham.csv"), index=False)
    print(f"[ingest] silvikultur_2024_ham.csv: {len(df)} satır (ulusal toplam dahil)")


def main():
    ingest_yillik_seri()
    ingest_il_dagilim()
    ingest_orman_alani()
    ingest_effis()
    ingest_bolge_2025()
    ingest_bolge_neden_2025()
    ingest_silvikultur_2024()


if __name__ == "__main__":
    main()
