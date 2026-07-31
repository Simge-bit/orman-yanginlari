from utils import load_config, data_path


def main():
    config = load_config()
    raw_dir = data_path("raw")
    print(f"[ingest] raw kaynaklar: {raw_dir}")
    # TODO Faz 1: OGM/EFFIS/TÜİK dosyalarını data/raw/ altında oku,
    # data/interim/ altına standart formatta (parquet/csv) yaz.


if __name__ == "__main__":
    main()
