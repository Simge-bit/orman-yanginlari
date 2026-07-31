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
}
