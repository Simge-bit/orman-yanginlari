import json
import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from utils import data_path, standardize_il  # noqa: E402


@pytest.fixture(scope="module")
def canonical_iller():
    geo = json.load(open(data_path("raw", "tr_iller.geojson"), encoding="utf-8"))
    return {standardize_il(f["properties"]["name"]) for f in geo["features"]}


def test_il_dagilim_81_il_ve_eslesme(canonical_iller):
    df = pd.read_csv(data_path("interim", "il_dagilim_2025.csv"))
    assert len(df) == 81
    assert not df["il"].duplicated().any()
    assert set(df["il"]) == canonical_iller


def test_orman_alani_81_il_ve_eslesme(canonical_iller):
    df = pd.read_csv(data_path("interim", "orman_alani_il.csv"))
    assert len(df) == 81
    assert set(df["il"]) == canonical_iller


def test_il_toplami_ulusal_toplamla_eslesiyor():
    il_df = pd.read_csv(data_path("interim", "il_dagilim_2025.csv"))
    yillik_df = pd.read_csv(data_path("interim", "yillik_seri.csv"))
    ulusal_2025 = yillik_df[yillik_df["yil"] == 2025].iloc[0]

    assert il_df["yangin_sayisi"].sum() == ulusal_2025["yangin_sayisi"]
    # OGM'nin Tablo 2.14 (il bazında) ile Tablo 2.11 (ulusal yıllık) arasında
    # ~0,5 ha'lık bilinen küçük bir yuvarlama farkı var.
    assert abs(il_df["yanan_alan_ha"].sum() - ulusal_2025["yanan_alan_ha"]) < 1.0


def test_yillik_seri_surekli_1988_guncel():
    df = pd.read_csv(data_path("interim", "yillik_seri.csv"))
    assert sorted(df["yil"]) == list(range(1988, int(df["yil"].max()) + 1))
    assert df["yangin_sayisi"].notna().all()
    assert df["yanan_alan_ha"].notna().all()


def test_effis_konfigurasyondaki_ulkeleri_iceriyor():
    from utils import load_config
    config = load_config()
    df = pd.read_csv(data_path("interim", "effis_ulke_karsilastirma.csv"))
    df_2024 = df[df["yil"] == 2024]
    assert set(config["karsilastirma_ulkeler"]) <= set(df_2024["ulke"].dropna())


def test_bolge_2025_toplami_ulusal_toplamla_yakin():
    bolge_df = pd.read_csv(data_path("interim", "bolge_yangin_2025.csv"))
    yillik_df = pd.read_csv(data_path("interim", "yillik_seri.csv"))
    ulusal_2025 = yillik_df[yillik_df["yil"] == 2025].iloc[0]

    assert bolge_df["yangin_sayisi"].sum() == ulusal_2025["yangin_sayisi"]
    # OGM'nin kendi Faaliyet Raporu'nda bölge tablosu (81.473,46) ile özet
    # tablosu (81.473) arasında ~0.5 ha'lık bilinen bir yuvarlama farkı var.
    assert abs(bolge_df["yanan_alan_ha"].sum() - ulusal_2025["yanan_alan_ha"]) < 1.0


def test_bolge_neden_2025_bolge_toplamiyla_eslesiyor():
    neden_df = pd.read_csv(data_path("interim", "bolge_neden_2025.csv"))
    bolge_df = pd.read_csv(data_path("interim", "bolge_yangin_2025.csv"))
    birlesik = neden_df.merge(bolge_df, on="bolge_muduru", suffixes=("_neden", "_toplam"))

    assert (birlesik["yangin_sayisi_neden"] == birlesik["yangin_sayisi_toplam"]).all()
    assert ((birlesik["yanan_alan_ha_neden"] - birlesik["yanan_alan_ha_toplam"]).abs() < 0.1).all()

    oran_kolonlari = [c for c in neden_df.columns if c.endswith("_sayi_oran")]
    assert (neden_df[oran_kolonlari].sum(axis=1).round(1) == 100.0).all()


def test_silvikultur_2025_bolge_toplami_ulusal_toplamla_eslesiyor():
    bolge_df = pd.read_csv(data_path("interim", "silvikultur_2025.csv"))
    yillik_df = pd.read_csv(data_path("interim", "yillik_seri.csv"))
    ulusal_2025 = yillik_df[yillik_df["yil"] == 2025].iloc[0]

    assert abs(bolge_df["toplam_alan_ha"].sum() - ulusal_2025["yanan_alan_ha"]) < 1.0

    bilesen_kolonlari = [
        "zarar_gormeyen_ha", "dogal_genclestirme_ha", "suni_genclestirme_ha",
        "rehabilitasyon_ha", "agaclandirma_ha", "koruma_ha", "gelecek_yillara_ha",
    ]
    # OGM'nin kendi tablosunda bir satırda (Balıkesir) ~0.55 ha'lık bilinen
    # bir yuvarlama farkı var (bkz. KAYNAKLAR.md) — tolerans buna göre.
    fark = (bolge_df[bilesen_kolonlari].sum(axis=1) - bolge_df["toplam_alan_ha"]).abs()
    assert (fark < 1.0).all()


def test_neden_bolge_2025_alt_kategoriler_toplamla_tutarli():
    df = pd.read_csv(data_path("interim", "neden_bolge_2025.csv"))
    alt_kategoriler = [
        "ihmal_aniz", "ihmal_copluk", "ihmal_avcilik_coban",
        "ihmal_sigara", "ihmal_piknik", "ihmal_diger",
        "kasit_teror", "kasit_kundaklama", "kasit_acma", "kasit_diger",
        "kaza_enerji", "kaza_trafik", "kaza_diger",
        "bilinmeyen", "dogal",
    ]
    # DKMPGM (Milli Parklar) satırında OGM'nin kendi tablosunda ~2.9 ha'lık
    # bilinen bir tutarsızlık var (bkz. KAYNAKLAR.md) — tolerans buna göre.
    fark_ha = (df[[f"{k}_ha" for k in alt_kategoriler]].sum(axis=1) - df["toplam_ha"]).abs()
    fark_sayi = (df[[f"{k}_sayi" for k in alt_kategoriler]].sum(axis=1) - df["toplam_sayi"]).abs()
    assert (fark_ha < 3.0).all()
    assert (fark_sayi < 1).all()


def test_bolge_cok_yillik_her_yil_ulusal_toplamla_tutarli():
    df = pd.read_csv(data_path("interim", "bolge_cok_yillik.csv"))
    yillik_df = pd.read_csv(data_path("interim", "yillik_seri.csv"))

    assert df["bolge_muduru"].nunique() == 31
    assert set(df["yil"]) == set(range(2004, 2026))

    bolge_yillik_toplam = df.groupby("yil")["alan_ha"].sum()
    for yil, toplam in bolge_yillik_toplam.items():
        ulusal = yillik_df[yillik_df["yil"] == yil].iloc[0]["yanan_alan_ha"]
        assert abs(toplam - ulusal) < 2.0, f"{yil}: bölge toplamı {toplam:.1f} != ulusal {ulusal:.1f}"


def test_vasif_dagilimi_2025_ulusal_bilesenleri_bilinen_sapma_icinde():
    # 2024'ün aksine (bileşenler toplamı ~birebir eşleşiyordu), 2025
    # tablosunda OGM'nin kendi verisinde kategoriler artık birbirini
    # dışlamıyor gibi görünüyor — ulusal düzeyde bileşen toplamı beyan
    # edilen alandan %13,5 fazla, bölge bazında fark çok daha büyük ve
    # tutarsız (bkz. KAYNAKLAR.md). Bu yüzden per-bölge sıkı eşitlik yerine
    # sadece ULUSAL satırın bilinen sapma aralığında kaldığını doğruluyoruz
    # (site de sadece bu ulusal satırı kullanıyor, bölge bazında vasıf
    # grafiği yok) — sapma beklenmedik şekilde büyürse bu test yakalar.
    ulusal = pd.read_csv(data_path("interim", "vasif_dagilimi_2025_ulusal.csv")).iloc[0]
    kategoriler = [
        "normal_koru_ha", "bosluklu_koru_ha", "normal_baltalik_ha",
        "bosluklu_baltalik_ha", "makilik_ha", "agaclandirma_sahasi_ha",
    ]
    fark_orani = (sum(ulusal[k] for k in kategoriler) - ulusal["toplam_ha"]) / ulusal["toplam_ha"]
    assert 0.10 < fark_orani < 0.20
