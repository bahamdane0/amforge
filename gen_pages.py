#!/usr/bin/env python3
import os
from build import page, write, ROOT, SITE_URL, BASE_PATH
from tools_catalog import TOOLS, LIVE_TOOLS, CATEGORIES

PRIVACY_LINE = """<div class="status-msg ok show" style="margin:0 0 20px;">
  🔒 Your files never leave your browser. All processing happens locally.
</div>"""

# --------------------------------------------------------------------------
# HOME
# --------------------------------------------------------------------------
def gen_home():
    popular = LIVE_TOOLS[:8]
    cards = "\n".join(f"""<a href="{BASE_PATH}/tools/{t['slug']}.html" class="card tool-card">
      <div class="icon">{t['name'][0]}</div>
      <h3>{t['name']}</h3>
      <p>{t['desc']}</p>
      <span class="go">Open tool →</span>
    </a>""" for t in popular)

    cat_cards = "\n".join(f"""<div class="card">
      <h3>{cat}</h3>
      <p>{len([t for t in TOOLS if t['cat']==cat])} tools for working with {cat} data.</p>
      <a class="go" href="{BASE_PATH}/tools.html#{cat.lower()}">Browse {cat} tools →</a>
    </div>""" for cat in CATEGORIES)

    body = f"""
<section class="hero">
  <div class="wrap">
    <div class="eyebrow"><span class="dot"></span> Free · No sign-up · Runs entirely in your browser</div>
    <h1>The free online data converter for JSON, CSV & Excel.</h1>
    <p class="lede">DataConverter Forge is a fast, free file converter and data converter that works entirely in your browser. Convert JSON, CSV, and Excel files instantly — no uploads, no server, no database, no data ever leaves your device.</p>
    <div class="hero-actions">
      <a href="{BASE_PATH}/tools.html" class="btn btn-primary">Browse all tools</a>
      <a href="{BASE_PATH}/tools/json-formatter.html" class="btn btn-secondary">Try JSON Formatter</a>
    </div>
    <div class="trust-line">
      <svg viewBox="0 0 24 24" fill="none" stroke-width="2"><path d="M5 12l5 5L19 7"/></svg>
      Files are processed with JavaScript in your tab and are never transmitted anywhere.
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="section-head">
      <div class="eyebrow"><span class="dot"></span> Popular</div>
      <h2>Start with a tool</h2>
      <p>The tools developers reach for most, ready with no setup.</p>
    </div>
    <div class="grid grid-4">{cards}</div>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="section-head">
      <div class="eyebrow"><span class="dot"></span> Categories</div>
      <h2>Organized by data type</h2>
    </div>
    <div class="grid grid-4">{cat_cards}</div>
  </div>
</section>

<section>
  <div class="wrap grid grid-2" style="align-items:center;">
    <div>
      <div class="eyebrow"><span class="dot"></span> Why DataConverter Forge</div>
      <h2>Built like an anvil, not a black box.</h2>
      <p>Most online converters ask you to upload your file to a server you can't see. DataConverter Forge doesn't. Every tool runs as plain JavaScript in the tab that's already open — your data is shaped and reshaped locally, then handed straight back to you.</p>
      <p>That means no waiting on uploads, no privacy policy to worry about for your file contents, and tools that work identically offline once the page has loaded.</p>
    </div>
    <div class="card" style="padding:30px;">
      <h3 style="margin-bottom:16px;">What stays local</h3>
      <ul class="prose" style="margin:0;">
        <li>The file you drop in</li>
        <li>Every intermediate conversion step</li>
        <li>The result you download</li>
      </ul>
      <p style="margin-top:16px;font-size:13px;">Only a daily usage counter is stored, locally, to keep the free plan sustainable.</p>
    </div>
  </div>
</section>

<section>
  <div class="wrap card" style="padding:40px;text-align:center;background:linear-gradient(160deg,var(--surface),var(--bg-elevated));">
    <h2 style="margin-bottom:10px;">Need more room to work?</h2>
    <p style="max-width:480px;margin:0 auto 20px;">DataConverter Forge Pro removes daily limits and raises the file-size ceiling for teams handling bigger exports.</p>
    <a href="{BASE_PATH}/pricing.html" class="btn btn-primary">See Pro plans</a>
  </div>
</section>
"""
    home_ld = f"""<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "WebSite",
  "name": "DataConverter Forge",
  "url": "{SITE_URL}/",
  "potentialAction": {{
    "@type": "SearchAction",
    "target": "{SITE_URL}/tools.html?q={{search_term_string}}",
    "query-input": "required name=search_term_string"
  }}
}}
</script>
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "DataConverter Forge",
  "url": "{SITE_URL}/",
  "logo": "{SITE_URL}/assets/img/favicon.svg"
}}
</script>"""
    write("/index.html", page(
        "DataConverter Forge — Free Online Data, CSV, Excel & JSON Converter",
        "Free online data converter and file converter for JSON, CSV, and Excel. Convert CSV to Excel, JSON to CSV, and more instantly in your browser — no uploads, no accounts, no data ever leaves your device.",
        "/", body, active_nav="/", extra_head=home_ld
    ))

# --------------------------------------------------------------------------
# ALL TOOLS
# --------------------------------------------------------------------------
def gen_tools_index():
    sections = []
    for cat in CATEGORIES:
        items = [t for t in TOOLS if t["cat"] == cat]
        cards = []
        for t in items:
            if t["live"]:
                cards.append(f"""<a href="{BASE_PATH}/tools/{t['slug']}.html" class="card tool-card">
                  <h3>{t['name']}</h3><p>{t['desc']}</p><span class="go">Open tool →</span>
                </a>""")
            else:
                cards.append(f"""<div class="card tool-card" style="opacity:.55;">
                  <h3>{t['name']}</h3><p>{t['desc']}</p><span class="go" style="color:var(--text-faint);">Coming soon</span>
                </div>""")
        sections.append(f"""<div id="{cat.lower()}" style="padding-top:30px;">
          <h2>{cat} tools</h2>
          <div class="grid grid-3">{''.join(cards)}</div>
        </div>""")

    body = f"""
<section class="tool-page-head">
  <div class="wrap">
    <div class="eyebrow"><span class="dot"></span> {len(LIVE_TOOLS)} tools live · {len(TOOLS)} planned</div>
    <h1>All data converter & file converter tools</h1>
    <p class="lede">Every data converter and file converter tool runs locally in your browser. Pick a category or jump straight to a tool.</p>
  </div>
</section>
<section style="padding-top:0;">
  <div class="wrap">{''.join(sections)}</div>
</section>
"""
    write("/tools.html", page(
        "Data Converter & File Converter Tools — JSON, CSV, Excel | DataConverter Forge",
        "Browse every data converter and file converter tool from DataConverter Forge: JSON, CSV, Excel, and developer utilities that run entirely in your browser.",
        "/tools.html", body, active_nav="/tools.html"
    ))

# --------------------------------------------------------------------------
# PRICING
# --------------------------------------------------------------------------
def gen_pricing():
    body = """
<section class="tool-page-head">
  <div class="wrap" style="text-align:center;">
    <div class="eyebrow" style="justify-content:center;"><span class="dot"></span> Simple pricing</div>
    <h1>Free today. Pro when you need more room.</h1>
    <p class="lede" style="margin:0 auto;">DataConverter Forge starts completely free with no account required. Pro is in development for teams that outgrow the daily limits.</p>
  </div>
</section>
<section style="padding-top:20px;">
  <div class="wrap grid grid-2" style="max-width:820px;">
    <div class="card pricing-card">
      <h3>Free</h3>
      <div class="price">$0<span> / forever</span></div>
      <p>Everything you need for everyday conversions.</p>
      <ul>
        <li>5 conversions per day</li>
        <li>Files up to 5 MB</li>
        <li>All standard tools</li>
        <li>No account required</li>
        <li>Dark and light mode</li>
      </ul>
      <a href="{BASE_PATH}/tools.html" class="btn btn-secondary" style="width:100%;">Start using DataConverter Forge</a>
    </div>
    <div class="card pricing-card highlight">
      <span class="badge">In development</span>
      <h3 style="margin-top:12px;">Pro</h3>
      <div class="price">$5<span> / month</span></div>
      <p>For heavier workloads and teams.</p>
      <ul>
        <li>Unlimited conversions</li>
        <li>Files up to 1 GB</li>
        <li>Batch conversion</li>
        <li>Advanced tools</li>
        <li>API access</li>
        <li>No ads, priority processing</li>
      </ul>
      <button class="btn btn-primary" style="width:100%;" disabled>Coming soon</button>
    </div>
  </div>
  <div class="wrap">
    <p class="center-note">Pro will require an account and a backend to verify subscriptions — the free tools you use today will keep working exactly as they do now.</p>
  </div>
</section>
"""
    write("/pricing.html", page(
        "Pricing — DataConverter Forge Free & Pro Plans",
        "DataConverter Forge is free with a 3-conversion daily limit. DataConverter Forge Pro ($5/month) removes limits and unlocks batch conversion and API access.",
        "/pricing.html", body, active_nav="/pricing.html"
    ))

# --------------------------------------------------------------------------
# ABOUT / PRIVACY / TERMS
# --------------------------------------------------------------------------
def gen_static_pages():
    about_body = """
<section class="tool-page-head">
  <div class="wrap prose" style="max-width:720px;">
    <div class="eyebrow"><span class="dot"></span> About</div>
    <h1>Why DataConverter Forge exists</h1>
    <p>Most "free" file-conversion sites work by uploading your file to a server before handing back a result. DataConverter Forge was built the opposite way: every tool runs as JavaScript inside the page you already have open, so your data never has to leave your device to be converted.</p>
    <h2>What we're building</h2>
    <p>DataConverter Forge started as a small set of JSON and CSV tools and is growing into a full developer-tools platform — one that stays free for everyday use and funds its growth through an optional Pro plan for heavier workloads.</p>
    <h2>How it stays free</h2>
    <p>Running DataConverter Forge costs nothing to host: it's static files on GitHub Pages, with no server or database to pay for. That's what lets the free plan exist without ads getting in the way of your work.</p>
  </div>
</section>
"""
    write("/about.html", page("About DataConverter Forge — Free, Local-First Data Tools",
        "Learn why DataConverter Forge processes every file locally in your browser instead of uploading it to a server.",
        "/about.html", about_body, active_nav="/about.html"))

    privacy_body = """
<section class="tool-page-head">
  <div class="wrap prose" style="max-width:720px;">
    <h1>Privacy Policy</h1>
    <p>Last updated 2026.</p>
    <h2>Your files</h2>
    <p>DataConverter Forge tools run entirely in your browser using JavaScript. When you use a conversion or formatting tool, the file or text you provide is processed on your device and is never uploaded, transmitted, or stored on any server operated by DataConverter Forge.</p>
    <h2>Local storage</h2>
    <p>DataConverter Forge stores two small pieces of information in your browser's local storage: your theme preference (dark or light) and a daily usage counter used to enforce the free plan's conversion limit. Neither includes the content of any file you process.</p>
    <h2>Analytics</h2>
    <p>If analytics are enabled in a future version, they will be limited to anonymous page-view counts and will never include file contents or personally identifying information.</p>
    <h2>Future accounts</h2>
    <p>If you choose to create a DataConverter Forge Pro account in the future, we will collect only the information required to manage your subscription (such as an email address and subscription status). This policy will be updated before that feature launches.</p>
    <h2>Contact</h2>
    <p>Questions about this policy can be sent to the contact details listed on our About page once published.</p>
  </div>
</section>
"""
    write("/privacy.html", page("Privacy Policy — DataConverter Forge",
        "DataConverter Forge never uploads your files. Read our privacy policy on local processing and local storage usage.",
        "/privacy.html", privacy_body, active_nav=""))

    terms_body = """
<section class="tool-page-head">
  <div class="wrap prose" style="max-width:720px;">
    <h1>Terms of Service</h1>
    <p>Last updated 2026.</p>
    <h2>Use of the service</h2>
    <p>DataConverter Forge is provided free of charge for personal and commercial use, subject to the daily usage limits described on our Pricing page. Tools are provided "as is" without warranty of any kind.</p>
    <h2>Your content</h2>
    <p>Because all processing happens locally in your browser, DataConverter Forge does not receive, store, or have access to the files or text you process, and makes no claim of ownership over them.</p>
    <h2>Fair use</h2>
    <p>Attempting to circumvent the free plan's usage limits through automated means is not permitted. A Pro plan for higher-volume use is planned.</p>
    <h2>Changes</h2>
    <p>These terms may be updated as DataConverter Forge adds features such as accounts and subscriptions. Continued use of the site after a change constitutes acceptance of the updated terms.</p>
  </div>
</section>
"""
    write("/terms.html", page("Terms of Service — DataConverter Forge",
        "Terms of service for using DataConverter Forge's free browser-based data conversion tools.",
        "/terms.html", terms_body, active_nav=""))

# --------------------------------------------------------------------------
# SEO / infra files
# --------------------------------------------------------------------------
def gen_infra():
    import datetime
    today = datetime.date.today().isoformat()
    core = [("/", "1.0", "weekly"), ("/tools.html", "0.9", "weekly"),
            ("/pricing.html", "0.5", "monthly"), ("/about.html", "0.4", "monthly"),
            ("/privacy.html", "0.2", "yearly"), ("/terms.html", "0.2", "yearly")]
    tool_urls = [(f"/tools/{t['slug']}.html", "0.8", "monthly") for t in LIVE_TOOLS]
    all_urls = core + tool_urls
    items = "\n".join(
        f"  <url><loc>{SITE_URL}{u}</loc><lastmod>{today}</lastmod>"
        f"<changefreq>{freq}</changefreq><priority>{pri}</priority></url>"
        for u, pri, freq in all_urls
    )
    sitemap = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{items}
</urlset>"""
    write("/sitemap.xml", sitemap)

    robots = f"""User-agent: *
Allow: /

Sitemap: {SITE_URL}/sitemap.xml
"""
    write("/robots.txt", robots)

if __name__ == "__main__":
    gen_home()
    gen_tools_index()
    gen_pricing()
    gen_static_pages()
    gen_infra()
    print("Base pages generated. Run gen_tool_pages.py next for /tools/*.html")
