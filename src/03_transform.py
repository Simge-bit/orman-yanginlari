from utils import load_config, data_path


def main():
    config = load_config()
    print("[transform] türetilmiş metrikler: ortalama büyüklük, hareketli ortalama, yoğunluk indeksi")
    # TODO Faz 3: config['hareketli_ort_penceresi'] ve config['esikler'] kullanarak
    # metrikleri hesapla, data/interim/ -> data/interim/ üzerine yaz.


if __name__ == "__main__":
    main()
