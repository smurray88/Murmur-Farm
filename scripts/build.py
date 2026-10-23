#!/usr/bin/env python3
"""Write the shared header, footer, news, FAQ, search tags and structured data
directly into every page.

Everything ends up as plain HTML, so Google and AI answer engines (which often
don't run JavaScript) can read the phone number, address, menu, news and FAQ.

Run it after editing this file, data/faq.json or data/news.json:
    python3 scripts/build.py
GitHub also runs it automatically (see .github/workflows/update-news.yml).
"""
import html
import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# LAUNCH SWITCH. Keep False while this is a test site: every page is marked
# "noindex" so search engines stay away. Set to True on the day murmurfarm.com
# points here (see README "Launch checklist").
LAUNCHED = False
# ---------------------------------------------------------------------------

LIVE_URL = "https://murmurfarm.com/"
PREVIEW_URL = "https://smurray88.github.io/Murmur-Farm/"
SITE_URL = LIVE_URL if LAUNCHED else PREVIEW_URL

FACEBOOK = "https://www.facebook.com/share/1CnTeYEJyW/"
MHBA = "https://marylandthoroughbred.com/cms/index.php/directory-home/22-murmur-farm"
MAPS = "https://www.google.com/maps/search/?api=1&query=1334+Stafford+Road+Darlington+MD+21034"
PHONE, PHONE_TEL = "(410) 836-3491", "+14108363491"
EMAIL = "murmurfarm@verizon.net"

NAV = [
    ("index.html", "Home"),
    ("blofeld.html", "Blofeld"),
    ("warrant.html", "Warrant"),
    ("history.html", "Our History"),
    ("news.html", "News"),
    ("gallery.html", "Gallery"),
    ("for-sale.html", "For Sale"),
]
PAGES = [p for p, _ in NAV] + ["contact.html"]
CRUMB = dict(NAV + [("contact.html", "Contact")])

# Photos the farm already had on murmurfarm.com. Once the GitHub job has copied
# them into photos/, pages use the local copy so they keep working after launch.
LEGACY_IMAGES = {
    "https://murmurfarm.com/Sign.jpg": "photos/sign.jpg",
    "https://murmurfarm.com/banner1.jpg": "photos/banner.jpg",
    "https://murmurfarm.com/Blofeld.jpg": "photos/blofeld.jpg",
    "https://murmurfarm.com/Warrant.jpg": "photos/warrant.jpg",
}
SIGN = "photos/sign.jpg" if (ROOT / "photos/sign.jpg").exists() else "https://murmurfarm.com/Sign.jpg"
SHARE_IMAGE = SIGN if SIGN.startswith("http") else SITE_URL + SIGN

MONTHS = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()
e = lambda t: html.escape(str(t), quote=True)


# ---------------------------------------------------------------- structured data
FARM_ID = LIVE_URL + "#farm"
BUSINESS = {
    "@context": "https://schema.org",
    "@type": "LocalBusiness",
    "@id": FARM_ID,
    "name": "Murmur Farm",
    "description": "Family-run Thoroughbred nursery and breeding farm on 131 acres in Darlington, Maryland, "
                   "offering boarding, breeding, foaling, layups and sales prep, and standing the stallions "
                   "Blofeld and Warrant.",
    "url": LIVE_URL,
    "image": SHARE_IMAGE,
    "telephone": "+1-410-836-3491",
    "faxNumber": "+1-410-836-3489",
    "email": EMAIL,
    "foundingDate": "1961",
    "founder": [{"@type": "Person", "name": "Allen Murray"}, {"@type": "Person", "name": "Audrey Murray"}],
    "address": {
        "@type": "PostalAddress",
        "streetAddress": "1334 Stafford Road",
        "addressLocality": "Darlington",
        "addressRegion": "MD",
        "postalCode": "21034",
        "addressCountry": "US",
    },
    "geo": {"@type": "GeoCoordinates", "latitude": 39.626205, "longitude": -76.183938},
    "hasMap": MAPS,
    "areaServed": ["Maryland", "Pennsylvania", "Delaware", "Mid-Atlantic United States"],
    "sameAs": [FACEBOOK, MHBA],
    "knowsAbout": ["Thoroughbred breeding", "Foaling", "Mare care", "Horse boarding", "Layups", "Sales preparation"],
    "makesOffer": [
        {"@type": "Offer", "itemOffered": {"@type": "Service", "name": n}}
        for n in ["Permanent and seasonal horse boarding (outside mares welcome)", "Thoroughbred breeding",
                  "Foaling with overnight watch", "Layups", "Sales preparation", "Stallion showings"]
    ],
}

STALLIONS = {
    "blofeld.html": ("Blofeld", 5000, "Quality Road – Storm Minstrel, by Storm Cat. Gray or roan, 2012, 16.1 hands. "
                                      "Undefeated Grade 2-winning juvenile and sire of 17 stakes horses."),
    "warrant.html": ("Warrant", 4500, "Constitution – Whisper Number, by First Samurai. Chestnut, 2018, 16.1 hands. "
                                      "Grade 3 winner of $1,102,833 and second in the Santa Anita Handicap (G1)."),
}


def stallion_ld(name, fee, desc):
    return {
        "@context": "https://schema.org",
        "@type": "Service",
        "name": f"{name}: 2026 stallion season at Murmur Farm",
        "serviceType": "Thoroughbred stallion breeding",
        "description": desc,
        "provider": {"@id": FARM_ID},
        "areaServed": "Mid-Atlantic United States",
        "offers": {
            "@type": "Offer",
            "price": str(fee),
            "priceCurrency": "USD",
            "description": "Live foal. Payable when foal stands and nurses.",
        },
    }


def breadcrumb_ld(page):
    if page == "index.html":
        return None
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": LIVE_URL},
            {"@type": "ListItem", "position": 2, "name": CRUMB.get(page, page), "item": LIVE_URL + page},
        ],
    }


def faq_ld(faq):
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q["q"], "acceptedAnswer": {"@type": "Answer", "text": q["a"]}}
            for q in faq
        ],
    }


# ---------------------------------------------------------------- page pieces
def head_block(page, title, desc, faq):
    url = SITE_URL + ("" if page == "index.html" else page)
    tags = ["<script>document.documentElement.classList.add('js')</script>"]
    if not LAUNCHED:
        tags.append('<meta name="robots" content="noindex, nofollow">')
    else:
        tags.append(f'<link rel="canonical" href="{url}">')
    tags += [
        '<meta property="og:type" content="website">',
        '<meta property="og:site_name" content="Murmur Farm">',
        f'<meta property="og:title" content="{e(title)}">',
        f'<meta property="og:description" content="{e(desc)}">',
        f'<meta property="og:url" content="{url}">',
        f'<meta property="og:image" content="{SHARE_IMAGE}">',
        '<meta property="og:image:alt" content="The Murmur Farm sign at the entrance on Stafford Road">',
        '<meta name="twitter:card" content="summary_large_image">',
        f'<meta name="twitter:image" content="{SHARE_IMAGE}">',
        '<meta name="geo.region" content="US-MD">',
        '<meta name="geo.placename" content="Darlington, Maryland">',
    ]
    blocks = [BUSINESS]
    if page == "index.html":
        blocks.append({"@context": "https://schema.org", "@type": "WebSite", "name": "Murmur Farm", "url": LIVE_URL})
        blocks.append(faq_ld(faq))
    if page in STALLIONS:
        blocks.append(stallion_ld(*STALLIONS[page]))
    crumb = breadcrumb_ld(page)
    if crumb:
        blocks.append(crumb)
    for b in blocks:
        tags.append('<script type="application/ld+json">' + json.dumps(b, ensure_ascii=False) + "</script>")
    return "<!-- seo:start (written by scripts/build.py) -->\n  " + "\n  ".join(tags) + "\n  <!-- seo:end -->"


def header_html(page):
    current = ' aria-current="page"'
    links = "".join(
        f'<a href="{p}"{current if p == page else ""}>{label}</a>' for p, label in NAV
    )
    cur = ' aria-current="page"' if page == "contact.html" else ""
    return (
        '<header id="site-header" class="site-header">\n'
        '  <div class="wrap">\n'
        '    <a class="brand" href="index.html" aria-label="Murmur Farm home">'
        '<span class="brand-mark" aria-hidden="true">M</span>'
        '<span class="brand-name">Murmur Farm<small>Darlington, Maryland</small></span></a>\n'
        '    <button class="menu-toggle" type="button" aria-label="Open menu" aria-expanded="false" aria-controls="nav">'
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">'
        '<path d="M4 7h16M4 12h16M4 17h16"/></svg></button>\n'
        f'    <nav class="nav" id="nav" aria-label="Main">{links}'
        f'<a class="btn btn-primary" href="contact.html"{cur}>Contact</a></nav>\n'
        "  </div>\n"
        "</header>"
    )


def footer_html():
    explore = "".join(f'<li><a href="{p}">{label}</a></li>' for p, label in NAV + [("contact.html", "Contact")])
    return (
        '<footer id="site-footer" class="site-footer">\n'
        '  <div class="wrap">\n'
        '    <div class="footer-grid">\n'
        "      <div><h2 class=\"footer-h\">Murmur Farm</h2><p>A family-run Thoroughbred nursery and breeding farm "
        "on 131 acres in Harford County, Maryland. Est. 1961. Outside mares welcome.</p></div>\n"
        '      <div><h2 class="footer-h">Visit</h2><address>1334 Stafford Road<br>Darlington, Maryland 21034</address>'
        f'<a href="{MAPS}">Get directions →</a></div>\n'
        f'      <div><h2 class="footer-h">Contact</h2><ul><li><a href="tel:{PHONE_TEL}">{PHONE}</a></li>'
        f'<li>Fax (410) 836-3489</li><li><a href="mailto:{EMAIL}">{EMAIL}</a></li>'
        f'<li><a href="{FACEBOOK}" rel="noopener">Facebook</a></li></ul></div>\n'
        f'      <div><h2 class="footer-h">Explore</h2><ul>{explore}</ul></div>\n'
        "    </div>\n"
        f'    <div class="footer-bottom"><span>© {date.today().year} Murmur Farm · Mrs. Audrey Murray</span>'
        f'<a href="{MHBA}">Member listing · Maryland Horse Breeders Association</a></div>\n'
        "  </div>\n"
        "</footer>"
    )


def news_items(news, limit):
    out = []
    for n in news[:limit]:
        y, m, _ = n["date"].split("-")
        when = f"{MONTHS[int(m) - 1]} {y}"
        out.append(
            f'<li><a href="{e(n["url"])}" rel="noopener"><small>{e(n["source"])} · '
            f'<time datetime="{n["date"]}">{when}</time></small><strong>{e(n["title"])}</strong></a></li>'
        )
    return "\n        ".join(out)


def faq_html(faq):
    return "\n        ".join(
        f'<details class="faq-item"><summary>{e(q["q"])}</summary><p>{e(q["a"])}</p></details>' for q in faq
    )


# ---------------------------------------------------------------- build
def build_page(path, faq, news):
    s = path.read_text()
    page = path.name
    title = html.unescape(re.search(r"<title>(.*?)</title>", s, re.S).group(1))
    m = re.search(r'<meta name="description" content="(.*?)">', s)
    desc = html.unescape(m.group(1)) if m else ""

    # Search tags + structured data, between the markers (first run: replace the old hand-written tags)
    block = head_block(page, title, desc, faq)
    if "<!-- seo:start" in s:
        s = re.sub(r"<!-- seo:start.*?<!-- seo:end -->", lambda _: block, s, flags=re.S)
    else:
        s = re.sub(r'\n  <meta (property="og:|name="twitter:|name="robots")[^\n]*', "", s)
        s = s.replace('  <meta name="theme-color"', "  " + block + '\n  <meta name="theme-color"', 1)

    s = re.sub(r'<header id="site-header".*?</header>', lambda _: header_html(page), s, flags=re.S)
    s = re.sub(r'<footer id="site-footer".*?</footer>', lambda _: footer_html(), s, flags=re.S)
    s = re.sub(
        r'(<ul class="news[^"]*"[^>]*data-news="(\d+)"[^>]*>).*?(</ul>)',
        lambda m: m.group(1) + "\n        " + news_items(news, int(m.group(2))) + "\n      " + m.group(3),
        s, flags=re.S,
    )
    s = re.sub(
        r'(<div class="faq[^"]*"[^>]*data-faq[^>]*>).*?(</div><!-- /faq -->)',
        lambda m: m.group(1) + "\n        " + faq_html(faq) + "\n      " + m.group(2),
        s, flags=re.S,
    )
    for remote, local in LEGACY_IMAGES.items():
        if (ROOT / local).exists():
            s = s.replace(remote, local)
    path.write_text(s)


def write_sitemap():
    urls = "".join(
        f"  <url><loc>{LIVE_URL}{'' if p == 'index.html' else p}</loc></url>\n" for p in PAGES
    )
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + "</urlset>\n"
    )
    robots = "User-agent: *\n" + ("Allow: /\n" if LAUNCHED else "Disallow: /\n") + f"\nSitemap: {LIVE_URL}sitemap.xml\n"
    (ROOT / "robots.txt").write_text(robots)


def main():
    faq = json.loads((ROOT / "data/faq.json").read_text())
    news = json.loads((ROOT / "data/news.json").read_text())
    for page in PAGES:
        p = ROOT / page
        if p.exists():
            build_page(p, faq, news)
    write_sitemap()
    print(f"Built {len(PAGES)} pages · {'LIVE' if LAUNCHED else 'TEST (noindex)'} · {len(news)} news · {len(faq)} FAQs")


if __name__ == "__main__":
    main()
