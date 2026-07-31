import yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# OGM tablolarının kullandığı resmi il adı kanonik kabul edilir. GeoJSON gibi
# başka kaynaklarda farklı yazılan iller burada eşlenir.
# Kaynak: data/raw/KAYNAKLAR.md — "Afyon" (GeoJSON) vs "Afyonkarahisar" (OGM).
IL_ALIASLARI = {
    "Afyon": "Afyonkarahisar",
}


def load_config(path: str = "config.yaml") -> dict:
    with open(ROOT / path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def data_path(*parts: str) -> Path:
    return ROOT.joinpath("data", *parts)


def standardize_il(name: str) -> str:
    name = name.strip()
    return IL_ALIASLARI.get(name, name)
