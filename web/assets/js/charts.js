// Chart.js tabanlı, "vurgu" (emphasis) desenli çizgi grafikler: yıllık ham
// değer soluk gri "bağlam", hareketli ortalama vurgu renginde "asıl nokta".
// Renkler references/palette.md'deki doğrulanmış paletten: seri-vurgu ve
// seri-baglam CSS değişkenleri (bkz. style.css), tema (açık/koyu) değişince
// otomatik güncellenir.

function cssDegisken(ad) {
  return getComputedStyle(document.documentElement).getPropertyValue(ad).trim();
}

// Hareketli ortalama serisinin son noktasına değeri yazan basit bir eklenti.
const sonDegerEtiketiEklentisi = {
  id: "sonDegerEtiketi",
  afterDatasetsDraw(chart) {
    const ds = chart.data.datasets[1];
    if (!ds) return;
    const meta = chart.getDatasetMeta(1);
    const sonNokta = meta.data[meta.data.length - 1];
    const sonDeger = ds.data[ds.data.length - 1];
    if (!sonNokta || sonDeger == null) return;

    const { ctx } = chart;
    ctx.save();
    ctx.font = "600 12px system-ui, -apple-system, sans-serif";
    ctx.fillStyle = cssDegisken("--metin-birincil");
    ctx.textBaseline = "middle";
    ctx.fillText(
      new Intl.NumberFormat("tr-TR", { maximumFractionDigits: 1 }).format(sonDeger),
      sonNokta.x + 8,
      sonNokta.y
    );
    ctx.restore();
  },
};

function cizgiKartiOlustur({ canvasId, yillar, hamDeger, maDeger, hamEtiket, maEtiket }) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;

  new Chart(ctx, {
    type: "line",
    data: {
      labels: yillar,
      datasets: [
        {
          label: hamEtiket,
          data: hamDeger,
          borderColor: cssDegisken("--seri-baglam"),
          borderWidth: 1.5,
          pointRadius: 0,
          pointStyle: "line",
          tension: 0.15,
          order: 2,
        },
        {
          label: maEtiket,
          data: maDeger,
          borderColor: cssDegisken("--seri-vurgu"),
          borderWidth: 2,
          pointRadius: 0,
          pointStyle: "line",
          tension: 0.15,
          order: 1,
        },
      ],
    },
    plugins: [sonDegerEtiketiEklentisi],
    options: {
      responsive: true,
      layout: { padding: { right: 64 } },
      interaction: { mode: "index", intersect: false },
      plugins: {
        legend: {
          position: "top",
          align: "start",
          labels: { color: cssDegisken("--metin-ikincil"), usePointStyle: true, pointStyleWidth: 14 },
        },
        tooltip: {
          backgroundColor: cssDegisken("--yuzey"),
          titleColor: cssDegisken("--metin-birincil"),
          bodyColor: cssDegisken("--metin-birincil"),
          borderColor: cssDegisken("--kenar"),
          borderWidth: 1,
          padding: 10,
          usePointStyle: true,
          callbacks: {
            label(context) {
              const deger = new Intl.NumberFormat("tr-TR", { maximumFractionDigits: 1 }).format(context.parsed.y);
              return `${context.dataset.label}: ${deger}`;
            },
          },
        },
      },
      scales: {
        x: {
          grid: { display: false },
          ticks: { color: cssDegisken("--metin-soluk"), maxTicksLimit: 12 },
        },
        y: {
          grid: { color: cssDegisken("--izgara") },
          ticks: {
            color: cssDegisken("--metin-soluk"),
            callback: (deger) => new Intl.NumberFormat("tr-TR").format(deger),
          },
        },
      },
    },
  });
}

function hexOpaklikEkle(hex, opaklik) {
  const temiz = hex.replace("#", "");
  const r = parseInt(temiz.substring(0, 2), 16);
  const g = parseInt(temiz.substring(2, 4), 16);
  const b = parseInt(temiz.substring(4, 6), 16);
  return `rgba(${r}, ${g}, ${b}, ${opaklik})`;
}

// %100'e tamamlanan yığılmış alan grafiği — neden kategorisi payları (part-to-whole).
// Kategorik renkler style.css'teki --kategori-1..4 (dataviz skill validate_palette.js ile
// doğrulandı). Katmanlar arasında yüzey renginde ince bir çizgi (2px "surface gap") var.
function yiginKartiOlustur({ canvasId, yillar, seriler }) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;

  const datasets = seriler.map((seri, i) => ({
    label: seri.label,
    data: seri.data,
    backgroundColor: hexOpaklikEkle(cssDegisken(seri.renkDegiskeni), 0.82),
    borderColor: cssDegisken("--yuzey"),
    borderWidth: 1,
    pointRadius: 0,
    tension: 0.15,
    fill: i === 0 ? "origin" : "-1",
  }));

  new Chart(ctx, {
    type: "line",
    data: { labels: yillar, datasets },
    options: {
      responsive: true,
      interaction: { mode: "index", intersect: false },
      plugins: {
        legend: {
          position: "top",
          align: "start",
          labels: { color: cssDegisken("--metin-ikincil"), boxWidth: 14, boxHeight: 14 },
        },
        tooltip: {
          backgroundColor: cssDegisken("--yuzey"),
          titleColor: cssDegisken("--metin-birincil"),
          bodyColor: cssDegisken("--metin-birincil"),
          borderColor: cssDegisken("--kenar"),
          borderWidth: 1,
          padding: 10,
          callbacks: {
            label(context) {
              return `${context.dataset.label}: %${new Intl.NumberFormat("tr-TR", { maximumFractionDigits: 1 }).format(context.parsed.y)}`;
            },
          },
        },
      },
      scales: {
        x: { grid: { display: false }, ticks: { color: cssDegisken("--metin-soluk"), maxTicksLimit: 12 } },
        y: {
          stacked: true,
          min: 0,
          max: 100,
          grid: { color: cssDegisken("--izgara") },
          ticks: { color: cssDegisken("--metin-soluk"), callback: (v) => `%${v}` },
        },
      },
    },
  });
}

// "Vurgu" (emphasis) desenli çok serili çizgi grafik: bir seri (ör. Türkiye) vurgu
// renginde ve kalın, diğerleri tek bir soluk gri tonda "bağlam" — kimlik hâlâ
// tooltip/legend/tablo üzerinden tam olarak ulaşılabilir.
function ulkeKartiOlustur({ canvasId, yillar, seriler }) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;

  const datasets = seriler.map((seri) => ({
    label: seri.label,
    data: seri.data,
    borderColor: seri.vurgu ? cssDegisken("--seri-vurgu") : cssDegisken("--seri-baglam"),
    borderWidth: seri.vurgu ? 2.5 : 1.25,
    pointRadius: 0,
    pointStyle: "line",
    tension: 0.15,
    order: seri.vurgu ? 1 : 2,
  }));

  new Chart(ctx, {
    type: "line",
    data: { labels: yillar, datasets },
    options: {
      responsive: true,
      layout: { padding: { right: 8 } },
      interaction: { mode: "index", intersect: false },
      plugins: {
        legend: {
          position: "top",
          align: "start",
          labels: { color: cssDegisken("--metin-ikincil"), usePointStyle: true, pointStyleWidth: 14 },
        },
        tooltip: {
          backgroundColor: cssDegisken("--yuzey"),
          titleColor: cssDegisken("--metin-birincil"),
          bodyColor: cssDegisken("--metin-birincil"),
          borderColor: cssDegisken("--kenar"),
          borderWidth: 1,
          padding: 10,
          usePointStyle: true,
          callbacks: {
            label(context) {
              if (context.parsed.y == null) return `${context.dataset.label}: veri yok`;
              return `${context.dataset.label}: ${new Intl.NumberFormat("tr-TR").format(context.parsed.y)} ha`;
            },
          },
        },
      },
      scales: {
        x: { grid: { display: false }, ticks: { color: cssDegisken("--metin-soluk"), maxTicksLimit: 12 } },
        y: {
          grid: { color: cssDegisken("--izgara") },
          ticks: { color: cssDegisken("--metin-soluk"), callback: (v) => new Intl.NumberFormat("tr-TR").format(v) },
        },
      },
    },
  });
}

// Yatay çubuk grafik — sıralama/magnitude verisi için (tek seri, tek hue).
// "En çok etkilenen il" gibi kategorik sıralamalarda tablodan çok daha
// okunaklı; renk kimlik değil büyüklük taşıdığı için tek vurgu rengi yeter.
function cubukKartiOlustur({ canvasId, etiketler, degerler, birim }) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;

  new Chart(ctx, {
    type: "bar",
    data: {
      labels: etiketler,
      datasets: [
        {
          data: degerler,
          backgroundColor: hexOpaklikEkle(cssDegisken("--seri-vurgu"), 0.85),
          borderRadius: 4,
          barThickness: 16,
        },
      ],
    },
    options: {
      indexAxis: "y",
      responsive: true,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: cssDegisken("--yuzey"),
          titleColor: cssDegisken("--metin-birincil"),
          bodyColor: cssDegisken("--metin-birincil"),
          borderColor: cssDegisken("--kenar"),
          borderWidth: 1,
          padding: 10,
          callbacks: {
            label(context) {
              const deger = new Intl.NumberFormat("tr-TR", { maximumFractionDigits: 1 }).format(context.parsed.x);
              return birim ? `${deger} ${birim}` : deger;
            },
          },
        },
      },
      scales: {
        x: {
          grid: { color: cssDegisken("--izgara") },
          ticks: { color: cssDegisken("--metin-soluk"), callback: (v) => new Intl.NumberFormat("tr-TR").format(v) },
        },
        y: {
          grid: { display: false },
          ticks: { color: cssDegisken("--metin-birincil") },
        },
      },
    },
  });
}

// Saçılım grafiği — iki sürekli değişken arasındaki ilişkiyi (korelasyonu)
// göstermek için doğru grafik türü; metinde geçen bir Pearson r'nin görsel
// karşılığı. Tek seri olduğu için tek vurgu rengiyle, il adı tooltip başlığında.
function saciliminOlustur({ canvasId, noktalar, xEtiket, yEtiket }) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;

  new Chart(ctx, {
    type: "scatter",
    data: {
      datasets: [
        {
          data: noktalar,
          backgroundColor: hexOpaklikEkle(cssDegisken("--seri-vurgu"), 0.55),
          borderColor: cssDegisken("--seri-vurgu"),
          borderWidth: 1,
          radius: 4,
          hoverRadius: 6,
        },
      ],
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: cssDegisken("--yuzey"),
          titleColor: cssDegisken("--metin-birincil"),
          bodyColor: cssDegisken("--metin-birincil"),
          borderColor: cssDegisken("--kenar"),
          borderWidth: 1,
          padding: 10,
          callbacks: {
            title: (context) => context[0]?.raw?.il ?? "",
            label(context) {
              const { x, y } = context.raw;
              const xMetni = new Intl.NumberFormat("tr-TR", { maximumFractionDigits: 1 }).format(x);
              const yMetni = new Intl.NumberFormat("tr-TR", { maximumFractionDigits: 2 }).format(y);
              return `${xEtiket}: %${xMetni} · ${yEtiket}: %${yMetni}`;
            },
          },
        },
      },
      scales: {
        x: {
          title: { display: true, text: `${xEtiket} (%)`, color: cssDegisken("--metin-soluk") },
          grid: { color: cssDegisken("--izgara") },
          ticks: { color: cssDegisken("--metin-soluk") },
        },
        y: {
          title: { display: true, text: `${yEtiket} (%)`, color: cssDegisken("--metin-soluk") },
          grid: { color: cssDegisken("--izgara") },
          ticks: { color: cssDegisken("--metin-soluk") },
        },
      },
    },
  });
}

// Bir <details class="tablo-goster"> içine basit bir veri tablosu basar —
// grafiğin erişilebilir/tablo karşılığı (dataviz: "a table view exists").
function tabloOlustur({ detailsId, basliklar, satirlar }) {
  const detaylar = document.getElementById(detailsId);
  if (!detaylar) return;

  const tablo = document.createElement("table");
  tablo.className = "veri-tablosu";

  const thead = document.createElement("thead");
  const baslikSatiri = document.createElement("tr");
  basliklar.forEach((baslik) => {
    const th = document.createElement("th");
    th.textContent = baslik;
    baslikSatiri.appendChild(th);
  });
  thead.appendChild(baslikSatiri);
  tablo.appendChild(thead);

  const tbody = document.createElement("tbody");
  satirlar.forEach((satir) => {
    const tr = document.createElement("tr");
    satir.forEach((hucre) => {
      const td = document.createElement("td");
      td.textContent = hucre;
      tr.appendChild(td);
    });
    tbody.appendChild(tr);
  });
  tablo.appendChild(tbody);

  detaylar.appendChild(tablo);
}
