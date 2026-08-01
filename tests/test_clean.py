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
    df = pd.read_csv(data_path("interim", "il_dagilim_2024.csv"))
    assert len(df) == 81
    assert not df["il"].duplicated().any()
    assert set(df["il"]) == canonical_iller


def test_orman_alani_81_il_ve_eslesme(canonical_iller):
    df = pd.read_csv(data_path("interim", "orman_alani_il.csv"))
    assert len(df) == 81
    assert set(df["il"]) == canonical_iller


def test_il_toplami_ulusal_toplamla_eslesiyor():
    il_df = pd.read_csv(data_path("interim", "il_dagilim_2024.csv"))
    yillik_df = pd.read_csv(data_path("interim", "yillik_seri.csv"))
    ulusal_2024 = yillik_df[yillik_df["yil"] == 2024].iloc[0]

    assert il_df["yangin_sayisi"].sum() == ulusal_2024["yangin_sayisi"]
    assert il_df["yanan_alan_ha"].sum() == ulusal_2024["yanan_alan_ha"]


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


def test_silvikultur_2024_bolge_toplami_ulusal_toplamla_eslesiyor():
    bolge_df = pd.read_csv(data_path("interim", "silvikultur_2024.csv"))
    yillik_df = pd.read_csv(data_path("interim", "yillik_seri.csv"))
    ulusal_2024 = yillik_df[yillik_df["yil"] == 2024].iloc[0]

    assert abs(bolge_df["toplam_alan_ha"].sum() - ulusal_2024["yanan_alan_ha"]) < 1.0

    bilesen_kolonlari = [
        "zarar_gormeyen_ha", "dogal_genclestirme_ha", "suni_genclestirme_ha",
        "rehabilitasyon_ha", "agaclandirma_ha", "koruma_ha", "gelecek_yillara_ha",
    ]
    # OGM'nin kendi tablosunda bir satırda (Balıkesir) ~0.55 ha'lık bilinen
    # bir yuvarlama farkı var (bkz. KAYNAKLAR.md) — tolerans buna göre.
    fark = (bolge_df[bilesen_kolonlari].sum(axis=1) - bolge_df["toplam_alan_ha"]).abs()
    assert (fark < 1.0).all()
