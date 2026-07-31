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
