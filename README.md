# Murmur Farm website

A modern, mobile-first redesign of [murmurfarm.com](https://murmurfarm.com) — plain HTML and CSS, no build step.

## Pages
| File | Page |
| --- | --- |
| `index.html` | Home: stallions, services, legacy |
| `blofeld.html` | Blofeld |
| `warrant.html` | Warrant |
| `history.html` | Allen & Audrey Murray, timeline, past stallions, press |
| `gallery.html` | Photo gallery |
| `for-sale.html` | Horses for sale (currently none) |
| `contact.html` | Phone, email, map |
| `default.html` | Redirects old `default.html` links to the home page |

## Common edits
- **Brand colors:** the first lines of `assets/styles.css` (`--green`, `--orange`).
- **Header, footer and menu:** `assets/site.js` (shared by every page).
- **Stud fees and stats:** edit the stallion page and the matching card in `index.html`.
- **Add photos:** put the image in `photos/`, then add a line to the `PHOTOS` list near the bottom of `gallery.html`.
- **Horses for sale:** replace the "No horses for sale" box in `for-sale.html`.

## Viewing it
GitHub Pages: **Settings → Pages → Deploy from a branch → `main` / root**. The site appears at `https://smurray88.github.io/Murmur-Farm/`.


**After editing `assets/styles.css` or `assets/site.js`**, bump the `?v=` number on those links in every page so phones don't keep showing the old version.

## How pages are built
The header, footer, news list, FAQ, search tags and structured data are written into every page by `scripts/build.py`, so search engines and AI tools can read them without running JavaScript.
- **Edit the FAQ:** `data/faq.json`. **Edit the menu or footer:** `scripts/build.py`.
- GitHub runs the build automatically whenever you push, and every morning after fetching news.

## Launch checklist (when murmurfarm.com should show this site)
This is a test site: every page carries `noindex` so Google stays away. On launch day:
1. In `scripts/build.py`, change `LAUNCHED = False` to `LAUNCHED = True` and push. This removes `noindex`, adds canonical links and opens `robots.txt`.
2. In `404.html`, change the three `/Murmur-Farm/` paths to `/`.
3. Repo **Settings → Pages → Custom domain**: enter `murmurfarm.com`, then follow GitHub's DNS instructions at the domain registrar. Tick **Enforce HTTPS** once it's available.
4. In Google Business Profile, confirm the website is `https://murmurfarm.com`.
5. In Google Search Console, add murmurfarm.com and submit `https://murmurfarm.com/sitemap.xml`.
