# Project website

Static pages for PatchProof. No build step, no framework, no external requests.

| File | Page |
|---|---|
| `index.html` | Overview: the problem, the three pieces, the demo, the honest "what a receipt does not prove" band. |
| `how-it-works.html` | Receipt lifecycle, the seven freshness states, data boundaries, agent-host boundaries. |
| `install.html` | Install from source, record a first check, optional global commands and Codex plugin, uninstall. |
| `limits.html` | Every known limitation, plus what has actually been tested. |
| `style.css` | The whole stylesheet. |

## Preview locally

From the repository root:

```sh
python -m http.server 8790 --bind 127.0.0.1
```

Open <http://127.0.0.1:8790/web/>. The receipt viewer is at <http://127.0.0.1:8790/site/>.

## Publishing

The pages are relative-linked and use no absolute paths, so the `web/` folder can be served as-is by GitHub Pages, Cloudflare Pages, Netlify or any static host. To publish with GitHub Pages, point the source at the `web` folder on the branch you want to serve.

Pages intentionally ship a strict Content-Security-Policy with `script-src 'none'`: the site has no JavaScript, so nothing can fail silently in the browser.

## Editing rules

- Every claim on these pages must be checkable against the repository. If a behaviour changes, change the page in the same pull request.
- Do not add analytics, cookies, external fonts, CDN links or tracking pixels.
- Keep the limits page honest. It is the most important page here.
