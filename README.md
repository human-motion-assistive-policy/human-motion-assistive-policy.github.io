# human-motion-assistive-policy.github.io

Project page for **Human Motion Assistive Policy**, built with the
[Nerfies / academic-project-page](https://github.com/nerfies/nerfies.github.io)
Bulma template (same layout as <https://hierarchicalpretraining.github.io/>).

## Structure

```
index.html          # the page — edit the sections marked with TODO
static/css, static/js   # Bulma + FontAwesome + carousel/slider assets (do not edit)
figs/               # put figures here (e.g. overview.png)
videos/             # put .mp4 videos here (teaser-1.mp4, result-1.mp4, ...)
.nojekyll           # tells GitHub Pages to serve static/ as-is
```

## Filling in content

Open `index.html` and search for `TODO`. Replace, in order:

1. **Title** and **venue/submission status** (hero section).
2. **Authors** and **affiliations**.
3. **Links** — arXiv, paper PDF, code, video. Set the `href="#"` attributes.
4. **Teaser videos** — drop `videos/teaser-1.mp4`, `videos/teaser-2.mp4`.
5. **Abstract** text.
6. **Method Overview** figure (`figs/overview.png`) and description.
7. **Results / Gallery** videos and captions.
8. **BibTeX** entry.

To add a video tile, copy one `<div class="column">` block and change the
`<source src="...">` and caption.

## Local preview

```bash
python3 -m http.server 8000
# open http://localhost:8000
```

## Publishing on GitHub Pages

Push to the `main` branch of a repo named
`human-motion-assistive-policy.github.io`, then in **Settings → Pages** set the
source to the `main` branch, root (`/`). The site goes live at
`https://human-motion-assistive-policy.github.io/`.
