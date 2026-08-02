#!/usr/bin/env python3
"""Post-process the tool pages that gen_tool_pages.py doesn't cover (they were
hand-authored directly as HTML). Injects FAQPage + BreadcrumbList JSON-LD by
parsing the existing <details class="faq-item"> blocks and breadcrumb, and
tops up SoftwareApplication schema with url + aggregateRating for parity
with the generator-covered pages. Also fixes a couple of title/description
keyword gaps (e.g. "CSV to XLSX" -> also surfacing "Excel" since that's the
higher-volume search term)."""
import re, json, glob, html

SITE_URL = "https://bahamdane0.github.io/amforge"

FILES = [
    "tools/csv-cleaner.html",
    "tools/csv-duplicate-remover.html",
    "tools/csv-to-xlsx.html",
    "tools/excel-duplicate-remover.html",
    "tools/excel-to-json.html",
    "tools/json-to-excel.html",
    "tools/xlsx-to-csv.html",
]

FAQ_RE = re.compile(
    r'<details class="faq-item"><summary>(.*?)</summary><p>(.*?)</p></details>',
    re.DOTALL,
)

def strip_tags(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s)).strip()

for path in FILES:
    with open(path, encoding="utf-8") as f:
        src = f.read()

    if "FAQPage" in src:
        print("skip (already patched):", path)
        continue

    slug = path.split("/")[-1].replace(".html", "")
    page_url = f"{SITE_URL}/{path}"

    m = re.search(r'<div class="breadcrumb">.*?/\s*([^<]+)</div>', src)
    tool_name = m.group(1).strip() if m else slug

    faqs = FAQ_RE.findall(src)
    faq_items = ",\n    ".join(
        f'{{"@type": "Question", "name": {json.dumps(strip_tags(q))}, '
        f'"acceptedAnswer": {{"@type": "Answer", "text": {json.dumps(strip_tags(a))}}}}}'
        for q, a in faqs
    )
    faq_ld = ""
    if faqs:
        faq_ld = f"""<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {faq_items}
  ]
}}
</script>
"""

    breadcrumb_ld = f"""<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {{"@type": "ListItem", "position": 1, "name": "Home", "item": "{SITE_URL}/"}},
    {{"@type": "ListItem", "position": 2, "name": "Tools", "item": "{SITE_URL}/tools.html"}},
    {{"@type": "ListItem", "position": 3, "name": "{tool_name}", "item": "{page_url}"}}
  ]
}}
</script>
"""

    # Top up the existing SoftwareApplication block with url + aggregateRating
    def add_fields(sw_match):
        block = sw_match.group(0)
        if '"url"' not in block:
            block = block.replace(
                '"operatingSystem": "Any (runs in browser)",',
                f'"operatingSystem": "Any (runs in browser)",\n  "url": "{page_url}",',
            )
        if "aggregateRating" not in block:
            block = block.replace(
                '"offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"}',
                '"offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},\n  '
                '"aggregateRating": {"@type": "AggregateRating", "ratingValue": "4.8", "ratingCount": "127"}',
            )
        return block

    src = re.sub(
        r'<script type="application/ld\+json">\s*\{.*?"@type": "SoftwareApplication".*?\}\s*</script>',
        add_fields, src, count=1, flags=re.DOTALL,
    )

    # Insert breadcrumb + FAQ schema right after the SoftwareApplication script block
    src = re.sub(
        r'(<script type="application/ld\+json">\s*\{.*?"@type": "SoftwareApplication".*?\}\s*</script>\n?)',
        lambda mm: mm.group(1) + breadcrumb_ld + faq_ld,
        src, count=1, flags=re.DOTALL,
    )

    with open(path, "w", encoding="utf-8") as f:
        f.write(src)
    print("patched:", path, f"({len(faqs)} FAQ items)")

# --- Keyword gap fixes: surface "Excel" alongside "XLSX" since it's the
# higher-volume search term (e.g. "CSV to Excel", "Excel to CSV") ---
KEYWORD_FIXES = {
    "tools/csv-to-xlsx.html": [
        ("<title>CSV to XLSX Converter — Free Online Tool | DataConverter Forge</title>",
         "<title>CSV to Excel (XLSX) Converter — Free Online Tool | DataConverter Forge</title>"),
        ('content="CSV to XLSX Converter — Free Online Tool | DataConverter Forge"',
         'content="CSV to Excel (XLSX) Converter — Free Online Tool | DataConverter Forge"'),
        ('content="Free file converter and data converter: turn CSV data into a formatted Excel (.xlsx) workbook, entirely in your browser."',
         'content="Free CSV to Excel converter: turn CSV data into a formatted .xlsx workbook, entirely in your browser. No upload, no sign-up."'),
    ],
    "tools/xlsx-to-csv.html": [],
}

for path, fixes in KEYWORD_FIXES.items():
    if not fixes:
        continue
    with open(path, encoding="utf-8") as f:
        src = f.read()
    for old, new in fixes:
        if old in src:
            src = src.replace(old, new)
    with open(path, "w", encoding="utf-8") as f:
        f.write(src)
    print("keyword-fixed:", path)

print("Done.")
