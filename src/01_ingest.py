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


def main():
    ingest_yillik_seri()
    ingest_il_dagilim()
    ingest_orman_alani()
    ingest_effis()


if __name__ == "__main__":
    main()
