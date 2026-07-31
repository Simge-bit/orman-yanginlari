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
