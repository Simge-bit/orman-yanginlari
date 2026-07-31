// Leaflet choropleth: il bazında yangın yoğunluk indeksi (yanan alan / orman
// alanı, %). Sıralı (sequential) mavi skala, 5 kova, references/palette.md
// sequential ramp adımlarından (100/250/400/550/700).

// GeoJSON'da "Afyon" geçiyor, OGM tablolarında (ve dolayısıyla cografi.json'da)
// "Afyonkarahisar" — bkz. src/utils.py IL_ALIASLARI / data/raw/KAYNAKLAR.md.
const GEOJSON_IL_ESLEME = { Afyon: "Afyonkarahisar" };

const YOGUNLUK_RENK_BASAMAKLARI = ["#cde2fb", "#86b6ef", "#3987e5", "#1c5cab", "#0d366b"];

function kovaSiniriHesapla(degerler, kovaSayisi) {
  const sirali = [...degerler].sort((a, b) => a - b);
  const sinirlar = [];
  for (let i = 1; i < kovaSayisi; i++) {
    const idx = Math.floor((sirali.length * i) / kovaSayisi);
    sinirlar.push(sirali[Math.min(idx, sirali.length - 1)]);
  }
  return sinirlar;
}

function kovaRengi(deger, sinirlar) {
  for (let i = 0; i < sinirlar.length; i++) {
    if (deger <= sinirlar[i]) return YOGUNLUK_RENK_BASAMAKLARI[i];
  }
  return YOGUNLUK_RENK_BASAMAKLARI[YOGUNLUK_RENK_BASAMAKLARI.length - 1];
}

async function haritayiCiz({ containerId, legendId }) {
  const [geojson, cografi] = await Promise.all([
    fetch("assets/data/tr_iller.geojson").then((r) => r.json()),
    veriYukle("cografi"),
  ]);

  const ilVerisi = new Map(cografi.iller.map((il) => [il.il, il]));
  const yogunlukDegerleri = cografi.iller.map((il) => il.yogunluk_indeksi_yuzde);
  const sinirlar = kovaSiniriHesapla(yogunlukDegerleri, YOGUNLUK_RENK_BASAMAKLARI.length);

  const harita = L.map(containerId, { scrollWheelZoom: false }).setView([39, 35.2], 6);

  function ilAdiGetir(feature) {
    const ad = feature.properties.name;
    return GEOJSON_IL_ESLEME[ad] || ad;
  }

  const katman = L.geoJSON(geojson, {
    style(feature) {
      const il = ilVerisi.get(ilAdiGetir(feature));
      return {
        fillColor: il ? kovaRengi(il.yogunluk_indeksi_yuzde, sinirlar) : "#ccc",
        weight: 1,
        color: cssDegisken("--yuzey"),
        fillOpacity: 0.9,
      };
    },
    onEachFeature(feature, layer) {
      const il = ilVerisi.get(ilAdiGetir(feature));
      if (!il) return;
      layer.bindTooltip(
        `<strong>${il.il}</strong><br>` +
          `Yangın: ${sayiFormatla(il.yangin_sayisi)} · Yanan alan: ${sayiFormatla(il.yanan_alan_ha)} ha<br>` +
          `Yoğunluk indeksi: %${sayiFormatla(il.yogunluk_indeksi_yuzde, 2)}`,
        { sticky: true }
      );
      layer.on("mouseover", () => layer.setStyle({ weight: 2.5, fillOpacity: 1 }));
      layer.on("mouseout", () => layer.setStyle({ weight: 1, fillOpacity: 0.9 }));
    },
  }).addTo(harita);

  harita.fitBounds(katman.getBounds());

  const legend = document.getElementById(legendId);
  if (legend) {
    const basamaklar = [0, ...sinirlar];
    legend.innerHTML = "";
    YOGUNLUK_RENK_BASAMAKLARI.forEach((renk, i) => {
      const satir = document.createElement("div");
      satir.className = "legend-satiri";
      const kutu = document.createElement("span");
      kutu.className = "legend-kutusu";
      kutu.style.background = renk;
      satir.appendChild(kutu);
      const ustSinir = sinirlar[i];
      const aciklama = ustSinir == null ? `> %${sayiFormatla(basamaklar[i], 2)}` : `%${sayiFormatla(basamaklar[i], 2)}–%${sayiFormatla(ustSinir, 2)}`;
      satir.appendChild(document.createTextNode(aciklama));
      legend.appendChild(satir);
    });
  }

  return harita;
}

// Canlı sıcak nokta katmanı (NASA FIRMS/VIIRS, CI'da periyodik çekilir —
// bkz. src/fetch_hotspots.py). 2024 yoğunluk haritasından tamamen farklı
// bir zaman dilimini gösterdiği için ayrı bir katman + ayrı efsane olarak,
// açıkça "canlı/son birkaç gün" etiketiyle sunuluyor. Yakın tespitler
// konum kümesi olarak geliyor (tespit_sayisi, en_yeni_saat_once) — "hâlâ
// aktif mi" garantisi veremeyiz ama taze/tekrarlı kümeleri koyu, eskiyenleri
// soluk göstererek kesinlik iddia etmeden bir sinyal veriyoruz.
function _kumeStili(nokta) {
  const saat = nokta.en_yeni_saat_once;
  // Sadece "taze" katman nabız atar — eskiyen kümeler de yanıp sönerse
  // rengin taşıdığı "bu daha az güncel" sinyali kaybolur.
  if (saat == null || saat <= 12) return { renk: "#d03b3b", opaklik: 0.9, agirlik: 1, nabiz: true };
  if (saat <= 36) return { renk: "#e37b5a", opaklik: 0.6, agirlik: 1, nabiz: false };
  return { renk: "#e3a58a", opaklik: 0.35, agirlik: 0.75, nabiz: false };
}

async function canliSicakNoktalariEkle({ harita, freshnessId, ilOzetiId }) {
  const veri = await fetch("assets/data/hotspots.json").then((r) => (r.ok ? r.json() : null));
  const freshnessYer = document.getElementById(freshnessId);
  const ilOzetiYer = ilOzetiId ? document.getElementById(ilOzetiId) : null;

  if (!veri) {
    if (freshnessYer) freshnessYer.textContent = "Canlı katman şu an yüklenemedi.";
    return;
  }

  const katman = L.layerGroup();
  veri.noktalar.forEach((nokta) => {
    const stil = _kumeStili(nokta);
    const yaricap = Math.min(4 + (nokta.maks_frp || 1) / 5 + Math.min(nokta.tespit_sayisi || 1, 8) / 2, 14);
    const saatMetni = nokta.en_yeni_saat_once != null ? `${sayiFormatla(nokta.en_yeni_saat_once, 1)} saat önce` : "bilinmiyor";

    L.circleMarker([nokta.latitude, nokta.longitude], {
      radius: yaricap,
      color: "#fff",
      weight: stil.agirlik,
      fillColor: stil.renk,
      fillOpacity: stil.opaklik,
      className: stil.nabiz ? "sicak-nokta-nabiz" : "",
    })
      .bindTooltip(
        `<strong>${nokta.yer ? `${nokta.yer}, ${nokta.il}` : nokta.il || "Konum belirlenemedi"}</strong><br>` +
          `Son görülme: ${saatMetni}<br>` +
          `Son ${veri.gun_araligi ?? 3} günde tespit: ${nokta.tespit_sayisi}` +
          (nokta.maks_frp != null ? `<br>En yüksek radyatif güç: ${nokta.maks_frp} MW` : "")
      )
      .addTo(katman);
  });
  katman.addTo(harita);

  if (freshnessYer) {
    const zaman = new Date(veri.guncelleme_zamani);
    const zamanMetni = zaman.toLocaleString("tr-TR", { dateStyle: "medium", timeStyle: "short", timeZone: "UTC" });
    const toplamTespit = veri.noktalar.reduce((t, n) => t + (n.tespit_sayisi || 1), 0);
    freshnessYer.textContent =
      veri.nokta_sayisi > 0
        ? `${veri.nokta_sayisi} farklı konumda sıcak nokta (toplam ${toplamTespit} uydu tespiti) · son ${veri.gun_araligi ?? 3} gün · koyu=taze (≤12 saat), soluk=eskiyen (>36 saat) · kaynak: ${veri.kaynak} · güncelleme: ${zamanMetni} UTC`
        : `Şu anda algılanan sıcak nokta yok · kaynak: ${veri.kaynak} · güncelleme: ${zamanMetni} UTC`;
  }

  if (ilOzetiYer) {
    ilOzetiYer.innerHTML = "";
    if (veri.nokta_sayisi > 0) {
      const ilSayilari = new Map();
      veri.noktalar.forEach((nokta) => {
        const ad = nokta.il || "İl belirlenemedi";
        ilSayilari.set(ad, (ilSayilari.get(ad) || 0) + (nokta.tespit_sayisi || 1));
      });
      const siraliIller = [...ilSayilari.entries()].sort((a, b) => b[1] - a[1]);
      const ILK_KAC_IL = 10;
      const gosterilen = siraliIller.slice(0, ILK_KAC_IL);
      const kalan = siraliIller.length - gosterilen.length;

      const baslik = document.createElement("strong");
      baslik.textContent = "İllere göre canlı tespit sayısı: ";
      ilOzetiYer.appendChild(baslik);
      ilOzetiYer.appendChild(
        document.createTextNode(
          gosterilen.map(([il, adet]) => `${il} (${adet})`).join(", ") + (kalan > 0 ? ` ve ${kalan} il daha` : "")
        )
      );
    }
  }
}
