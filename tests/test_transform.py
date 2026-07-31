import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from utils import data_path  # noqa: E402


def test_neden_oranlari_yuzde_100e_topluyor():
    df = pd.read_csv(data_path("interim", "yillik_metrikler.csv"))
    df = df[df["neden_kirilimi_var"]]

    sayi_toplam = df[[c for c in df.columns if c.endswith("_sayi_oran")]].sum(axis=1)
    alan_toplam = df[[c for c in df.columns if c.endswith("_alan_oran")]].sum(axis=1)

    # Tolerans 0.1: 2013 yılında OGM kaynağının kendi tablosunda ~0.5 ha'lık
    # bilinen bir yuvarlama farkı var (bkz. 02_clean.py çıktısındaki uyarı).
    assert ((sayi_toplam - 100).abs() < 0.1).all()
    assert ((alan_toplam - 100).abs() < 0.1).all()


def test_il_yogunluk_indeksi_makul_araliklarda():
    df = pd.read_csv(data_path("interim", "il_metrikler.csv"))
    assert df["yogunluk_indeksi_yuzde"].notna().all()
    assert (df["yogunluk_indeksi_yuzde"] >= 0).all()
    assert (df["yogunluk_indeksi_yuzde"] < 5).all()  # bir yılda ilin orman alanının >%5'i yanmış olması olağandışı olur


def test_ulke_alan_payi_her_yil_100e_topluyor():
    df = pd.read_csv(data_path("interim", "ulke_metrikler.csv"))
    yillik_toplam = df.dropna(subset=["alan_payi_yuzde"]).groupby("yil")["alan_payi_yuzde"].sum()
    assert (yillik_toplam.round(3) == 100).all()
