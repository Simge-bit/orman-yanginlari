// Ortak header/footer'ı enjekte eder ve JSON veri çekme yardımcılarını sağlar.
// Her sayfa <body data-page="..."> ile kendi sayfa kimliğini bildirir.

async function ortakParcalariYukle() {
  const sayfa = document.body.dataset.page;

  const [headerHtml, footerHtml] = await Promise.all([
    fetch("components/header.html").then((r) => r.text()),
    fetch("components/footer.html").then((r) => r.text()),
  ]);

  const headerYer = document.getElementById("site-header");
  const footerYer = document.getElementById("site-footer");
  if (headerYer) headerYer.innerHTML = headerHtml;
  if (footerYer) footerYer.innerHTML = footerHtml;

  if (sayfa) {
    const aktifLink = document.querySelector(`nav a[data-nav="${sayfa}"]`);
    if (aktifLink) aktifLink.setAttribute("aria-current", "page");
  }

  const menuDugmesi = document.getElementById("menu-dugmesi");
  const nav = document.getElementById("site-nav");
  if (menuDugmesi && nav) {
    menuDugmesi.addEventListener("click", () => {
      const acik = nav.classList.toggle("acik");
      menuDugmesi.setAttribute("aria-expanded", acik ? "true" : "false");
    });
  }
}

async function veriYukle(ad) {
  const res = await fetch(`assets/data/${ad}.json`);
  if (!res.ok) {
    throw new Error(`${ad}.json yüklenemedi (HTTP ${res.status})`);
  }
  return res.json();
}

function sayiFormatla(deger, ondalik = 0) {
  return new Intl.NumberFormat("tr-TR", {
    minimumFractionDigits: ondalik,
    maximumFractionDigits: ondalik,
  }).format(deger);
}

// p-değeri çok küçükse (ör. 0,0000038) sabit ondalıkla yuvarlayınca "p=0,0000"
// gibi yanıltıcı görünür — eşik altında kalanlar "p<0,0001" olarak gösterilir.
function pDegeriFormatla(p) {
  return p < 0.0001 ? "p<0,0001" : `p=${sayiFormatla(p, 4)}`;
}

// Dış kaynaklı metni (ör. Nominatim yer adları) HTML string'lerine
// enjekte etmeden önce kaçışlamak için — tooltip'ler innerHTML kullanıyor.
function htmlKacisla(metin) {
  const div = document.createElement("div");
  div.textContent = metin ?? "";
  return div.innerHTML;
}

document.addEventListener("DOMContentLoaded", ortakParcalariYukle);
