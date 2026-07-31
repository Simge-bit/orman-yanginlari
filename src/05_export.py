from utils import load_config, data_path


def main():
    config = load_config()
    processed_dir = data_path("processed")
    print(f"[export] JSON çıktıları: {processed_dir}")
    # TODO Faz 4: her sayfa için ozet.json, trend.json, cografi.json,
    # nedenler.json, karsilastirma.json, metodoloji.json üret ve
    # web/assets/data/ altına kopyala. Şemayı burada dondur.


if __name__ == "__main__":
    main()
