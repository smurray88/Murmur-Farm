// Shared header, footer and small interactions for every page.
(function () {
  var FACEBOOK = "https://www.facebook.com/share/1CnTeYEJyW/";
  var pages = [
    ["index.html", "Home"],
    ["blofeld.html", "Blofeld"],
    ["warrant.html", "Warrant"],
    ["history.html", "Our History"],
    ["news.html", "News"],
    ["gallery.html", "Gallery"],
    ["for-sale.html", "For Sale"]
  ];
  var here = location.pathname.split("/").pop() || "index.html";

  var navLinks = pages.map(function (p) {
    var cur = p[0] === here ? ' aria-current="page"' : "";
    return '<a href="' + p[0] + '"' + cur + ">" + p[1] + "</a>";
  }).join("");
  var contactCur = here === "contact.html" ? ' aria-current="page"' : "";

  var header = document.getElementById("site-header");
  if (header) {
    header.className = "site-header";
    header.innerHTML =
      '<div class="wrap">' +
        '<a class="brand" href="index.html" aria-label="Murmur Farm home">' +
          '<span class="brand-mark" aria-hidden="true">M</span>' +
          '<span class="brand-name">Murmur Farm<small>Darlington, Maryland</small></span>' +
        "</a>" +
        '<button class="menu-toggle" aria-label="Open menu" aria-expanded="false" aria-controls="nav">' +
          '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M4 7h16M4 12h16M4 17h16"/></svg>' +
        "</button>" +
        '<nav class="nav" id="nav">' + navLinks +
          '<a class="btn btn-primary" href="contact.html"' + contactCur + ">Contact</a>" +
        "</nav>" +
      "</div>";

    var toggle = header.querySelector(".menu-toggle");
    var nav = header.querySelector(".nav");
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  var footer = document.getElementById("site-footer");
  if (footer) {
    footer.className = "site-footer";
    footer.innerHTML =
      '<div class="wrap">' +
        '<div class="footer-grid">' +
          "<div><h4>Murmur Farm</h4><p>A family-run Thoroughbred nursery and breeding farm on 131 acres in Harford County, Maryland. Est. 1961.</p></div>" +
          "<div><h4>Visit</h4><p>1334 Stafford Road<br>Darlington, Maryland 21034</p>" +
            '<a href="https://www.google.com/maps/search/?api=1&query=1334+Stafford+Road+Darlington+MD+21034">Get directions →</a></div>' +
          '<div><h4>Contact</h4><ul><li><a href="tel:+14108363491">(410) 836-3491</a></li><li>Fax (410) 836-3489</li><li><a href="mailto:murmurfarm@verizon.net">murmurfarm@verizon.net</a></li><li><a href="' + FACEBOOK + '" rel="noopener">Facebook</a></li></ul></div>' +
          '<div><h4>Explore</h4><ul>' + pages.map(function (p) { return '<li><a href="' + p[0] + '">' + p[1] + "</a></li>"; }).join("") + "</ul></div>" +
        "</div>" +
        '<div class="footer-bottom"><span>© ' + new Date().getFullYear() + " Murmur Farm · Mrs. Audrey Murray</span>" +
          '<a href="https://marylandthoroughbred.com/cms/index.php/directory-home/22-murmur-farm">Member listing · Maryland Horse Breeders Association</a></div>' +
      "</div>";
  }

  // News & Results: any <ul data-news="N"> is filled from data/news.json,
  // which a GitHub Action refreshes every day.
  var MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
  function esc(t) { var d = document.createElement("div"); d.textContent = t; return d.innerHTML; }
  document.querySelectorAll("[data-news]").forEach(function (list) {
    var limit = parseInt(list.getAttribute("data-news"), 10) || 20;
    fetch("data/news.json", { cache: "no-cache" })
      .then(function (r) { return r.json(); })
      .then(function (items) {
        list.innerHTML = items.slice(0, limit).map(function (n) {
          var p = n.date.split("-");
          var when = MONTHS[parseInt(p[1], 10) - 1] + " " + p[0];
          return '<li><a href="' + esc(n.url) + '" rel="noopener"><small>' + esc(n.source) + " · " + when +
            "</small><strong>" + esc(n.title) + "</strong></a></li>";
        }).join("");
      })
      .catch(function () { list.innerHTML = '<li class="muted">News is unavailable right now.</li>'; });
  });

  // Gentle fade-in on scroll
  var els = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); } });
    }, { threshold: 0.12 });
    els.forEach(function (el) { io.observe(el); });
  } else {
    els.forEach(function (el) { el.classList.add("in"); });
  }

  // Hide images that fail to load so the green backdrop shows instead
  document.querySelectorAll("img[data-fallback]").forEach(function (img) {
    img.addEventListener("error", function () { img.style.display = "none"; });
  });
})();
