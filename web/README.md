# Project website

Static pages for PatchProof. No build step, no framework, no external requests.

| File | Page |
|---|---|
| `index.html` | Overview: the problem, the three pieces, the demo, the honest "what a receipt does not prove" band. |
| `how-it-works.html` | Receipt lifecycle, the seven freshness states, data boundaries, agent-host boundaries. |
| `install.html` | Install from source, record a first check, optional global commands and Codex plugin, uninstall. |
| `limits.html` | Every known limitation, plus what has actually been tested. |
| `style.css` | The whole stylesheet. |
| `og.png` | 1200×630 social preview, referenced by every page's `og:image`. |

The social preview is a real render of the overview page, not a mock-up. To refresh it after a layout change, screenshot the top 1200×630 of `index.html` at that viewport size and replace the file. Keep it above 20 KB — the checks fail on a missing or placeholder image.

## Preview locally

From the repository root:

```sh
python -m http.server 8790 --bind 127.0.0.1
```

Open <http://127.0.0.1:8790/web/>. The receipt viewer is at <http://127.0.0.1:8790/site/>.

## Publishing

`.github/workflows/pages.yml` publishes these pages to GitHub Pages on every push to `main` that touches `web/` or `assets/`. It assembles a `_site/` bundle, re-runs the link and policy checks against the assembled output, then deploys. Expected address: <https://parthiv-kota.github.io/patchproof/>.

In the repository settings, set **Pages → Build and deployment → Source** to **GitHub Actions** once. After that the workflow owns the site.

Any static host works too: the pages are relative-linked and use no absolute paths.

Pages intentionally ship a strict Content-Security-Policy with `script-src 'none'`: the site has no JavaScript, so nothing can fail silently in the browser.

## Editing rules

- Every claim on these pages must be checkable against the repository. If a behaviour changes, change the page in the same pull request.
- Do not add analytics, cookies, external fonts, CDN links or tracking pixels.
- Keep the limits page honest. It is the most important page here.
