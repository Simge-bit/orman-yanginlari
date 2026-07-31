import yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_config(path: str = "config.yaml") -> dict:
    with open(ROOT / path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def data_path(*parts: str) -> Path:
    return ROOT.joinpath("data", *parts)
