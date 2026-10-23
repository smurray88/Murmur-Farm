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
GitHub Pages: **Settings → Pages → Deploy from a branch → `main` / root**. The site appears at `https://smurray88.github.io/murmur-farm/`.

Images are currently linked from the existing murmurfarm.com site. Before pointing the murmurfarm.com domain here, copy those images into `photos/` and update the links.

**After editing `assets/styles.css` or `assets/site.js`**, bump the `?v=` number on those links in every page so phones don't keep showing the old version.
