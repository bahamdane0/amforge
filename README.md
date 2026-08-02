# DataConverter Forge

Free, browser-only developer data tools (JSON / CSV / Excel / dev utilities).
No backend, no database, no file uploads — everything runs as static HTML/CSS/JS.

## What's here

- **15 fully working tools** under `/tools/` (JSON Formatter, JSON Validator,
  JSON Minifier, JSON↔CSV, CSV Viewer, Base64 encode/decode, URL encode/decode,
  UUID Generator, Hash Generator, Regex Tester, Markdown Preview, JSON→TypeScript).
- **25 more tools cataloged** in `tools_catalog.py` and listed as "coming soon"
  on `/tools.html` — add a page for any of them by following the pattern below.
- Local, per-day usage limiter (5 free conversions/day, 5MB file cap) with the
  architecture already split so a future Pro/paid tier just swaps `Plan.current`
  for a real subscription check (`assets/js/main.js`).
- Dark/light mode, responsive layout, SEO metadata (Open Graph, Twitter cards,
  JSON-LD, canonical URLs, sitemap.xml, robots.txt) on every page.

## Project structure

```
/index.html, /tools.html, /pricing.html, /about.html, /privacy.html, /terms.html
/tools/*.html            ← one page per live tool
/assets/css/style.css    ← full design system
/assets/js/main.js       ← theme toggle + usage-limit engine (Usage, Plan)
/assets/js/tool-runtime.js ← generic workspace wiring shared by every tool page
/sitemap.xml, /robots.txt
build.py, gen_pages.py, gen_tool_pages.py, tools_catalog.py  ← page generators (dev-only)
```

The `build.py` / `gen_pages.py` / `gen_tool_pages.py` scripts are **authoring
tools only** — they regenerate the static `.html` files so the header, footer,
and SEO boilerplate stay consistent. Nothing in `/tools/`, `/index.html`, etc.
needs a build step to be *served*; deploy the generated files as-is.

## Adding a new tool

1. Add an entry to `TOOLS` in `tools_catalog.py` with `"live": True`.
2. In `gen_tool_pages.py`, call `tool_page(slug, workspace_html, transform_js, content, related, faqs)`
   — reuse `STD_WORKSPACE` for a simple textarea-in/textarea-out tool, or write
   a custom workspace (see `csv-viewer` or `regex-tester` for examples).
3. Run:
   ```bash
   python3 gen_pages.py && python3 gen_tool_pages.py
   ```
4. Commit the newly generated `/tools/<slug>.html`.

## Deploying to GitHub Pages (free)

1. Push this repository to GitHub.
2. In the repo, go to **Settings → Pages**.
3. Under "Build and deployment", set **Source** to `Deploy from a branch`,
   branch `main`, folder `/ (root)`.
4. Save. Your site will be live at `https://<username>.github.io/<repo>/`.
5. (Optional) Add a custom domain under Pages settings, then update `SITE_URL`
   in `build.py` and re-run the generators so canonical URLs, sitemap, and
   Open Graph tags point at the real domain.

## Deploying to Cloudflare Pages (free, alternative)

1. Push to GitHub.
2. In Cloudflare Pages, "Create a project" → connect the repo.
3. Build command: leave empty. Build output directory: `/` (repo root).
4. Deploy — Cloudflare will serve the static files directly.

## Roadmap toward DataConverter Forge Pro

The free-tier limiter (`Usage`) and plan lookup (`Plan`) in `assets/js/main.js`
are intentionally isolated so a paid tier can be added later without touching
any tool's logic:

- Replace `Plan.current` with a real check against a signed subscription token
  (issued by a backend after a PayPal subscription is confirmed).
- Add a lightweight backend + database only for: accounts, subscription
  status, and PayPal webhook verification. Tool logic itself never needs a
  backend — it will keep running client-side even for Pro users.
- Batch conversion, advanced tools, and API access are additive — they can
  ship as new tool pages / a new `/api` surface without restructuring what's
  here.

## Privacy

Every tool processes data with JavaScript already running in the page.
No file or text you convert is uploaded, transmitted, or stored on a server.
The only thing saved locally is your theme preference and a daily usage
counter (see `privacy.html`).
