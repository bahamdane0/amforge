#!/usr/bin/env python3
"""Generates all static HTML pages for DataConverter Forge from shared partials.
Run: python3 build.py   (regenerates every .html file in the repo)
No build step is required to *deploy* — the generated .html files are
committed and served as-is on GitHub Pages. This script just keeps the
repeated header/footer/SEO boilerplate consistent while authoring.
"""
import os, json, re

ROOT = os.path.dirname(os.path.abspath(__file__))
# GitHub Pages project site: served at https://bahamdane0.github.io/amforge/
# so every internal link needs the "/amforge" prefix. If a custom domain
# (e.g. amforge.dev) is set up later via CNAME, just set BASE_PATH = "" and
# SITE_URL to the custom domain.
BASE_PATH = "/amforge"
SITE_URL = "https://bahamdane0.github.io" + BASE_PATH

LOGO_SVG = """<svg class="mark" viewBox="0 0 26 26" xmlns="http://www.w3.org/2000/svg">
<path d="M4 18 L11 18 L15 8 L19 8" />
<path d="M11 18 L15 22" />
<circle class="spark" cx="19.5" cy="6.5" r="1.1"/>
<circle class="spark" cx="22" cy="9" r="0.8"/>
</svg>"""

NAV_LINKS = [
    (f"{BASE_PATH}/", "Home"),
    (f"{BASE_PATH}/tools.html", "All Tools"),
    (f"{BASE_PATH}/pricing.html", "Pricing"),
    (f"{BASE_PATH}/about.html", "About"),
]

def header(active=""):
    links = "\n".join(
        f'<a href="{href}" {"class=\"active\"" if active==href else ""}>{label}</a>'
        for href, label in NAV_LINKS
    )
    return f"""<header class="site-header">
  <div class="wrap">
    <a href="{BASE_PATH}/" class="brand">{LOGO_SVG}<span>DataConverter Forge</span></a>
    <nav class="main-nav" data-main-nav>
      {links}
    </nav>
    <div class="nav-actions">
      <button class="theme-toggle" data-theme-toggle aria-label="Toggle theme">☀</button>
      <button class="menu-toggle" data-menu-toggle aria-label="Menu" aria-expanded="false">
        <svg viewBox="0 0 24 24" class="icon-burger" xmlns="http://www.w3.org/2000/svg">
          <line x1="3" y1="6" x2="21" y2="6"/>
          <line x1="3" y1="12" x2="21" y2="12"/>
          <line x1="3" y1="18" x2="21" y2="18"/>
        </svg>
        <svg viewBox="0 0 24 24" class="icon-close" xmlns="http://www.w3.org/2000/svg">
          <line x1="5" y1="5" x2="19" y2="19"/>
          <line x1="19" y1="5" x2="5" y2="19"/>
        </svg>
      </button>
    </div>
  </div>
  <div class="nav-backdrop" data-nav-backdrop></div>
</header>"""

def footer():
    return f"""<footer class="site-footer">
  <div class="wrap">
    <div class="footer-grid">
      <div>
        <a href="{BASE_PATH}/" class="brand">{LOGO_SVG}<span>DataConverter Forge</span></a>
        <p style="margin-top:12px;max-width:280px;">Free browser-based data tools for developers. Your files never leave your device.</p>
      </div>
      <div>
        <h4>Tools</h4>
        <ul>
          <li><a href="{BASE_PATH}/tools/json-formatter.html">JSON Formatter</a></li>
          <li><a href="{BASE_PATH}/tools/json-to-csv.html">JSON to CSV</a></li>
          <li><a href="{BASE_PATH}/tools/base64-encoder.html">Base64 Encoder</a></li>
          <li><a href="{BASE_PATH}/tools.html">View all tools →</a></li>
        </ul>
      </div>
      <div>
        <h4>Company</h4>
        <ul>
          <li><a href="{BASE_PATH}/about.html">About</a></li>
          <li><a href="{BASE_PATH}/pricing.html">Pricing</a></li>
        </ul>
      </div>
      <div>
        <h4>Legal</h4>
        <ul>
          <li><a href="{BASE_PATH}/privacy.html">Privacy Policy</a></li>
          <li><a href="{BASE_PATH}/terms.html">Terms of Service</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-bottom">
      <span>© 2026 DataConverter Forge. All processing happens locally in your browser.</span>
      <span>Built for developers, by developers.</span>
    </div>
  </div>
</footer>"""

def page(title, description, path, body, active_nav="", extra_head="", canonical=None):
    canonical = canonical or f"{SITE_URL}{path}"
    og_image = f"{SITE_URL}/assets/img/favicon.svg"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{description}">
<meta name="google-site-verification" content="lpZYD8kohCjuw-RktrAJ48OkOUrG-nATKrGRQAQKpBc" />
<link rel="canonical" href="{canonical}">
<link rel="icon" href="{BASE_PATH}/assets/img/favicon.svg" type="image/svg+xml">

<meta property="og:type" content="website">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{og_image}">
<meta property="og:site_name" content="DataConverter Forge">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{description}">
<meta name="twitter:image" content="{og_image}">

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{BASE_PATH}/assets/css/style.css">
{extra_head}
</head>
<body>
{header(active_nav)}
<main>
{body}
</main>
{footer()}
<script src="{BASE_PATH}/assets/js/main.js"></script>
</body>
</html>"""

def write(path, html):
    full = os.path.join(ROOT, path.lstrip("/"))
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(html)
    print("wrote", path)

if __name__ == "__main__":
    print("This module is imported by the page-authoring scripts; run gen_pages.py instead.")
