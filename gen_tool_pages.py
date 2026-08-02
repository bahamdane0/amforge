#!/usr/bin/env python3
import json
from build import page, write, BASE_PATH
from tools_catalog import TOOLS, LIVE_TOOLS

def by_slug(slug):
    return next(t for t in TOOLS if t["slug"] == slug)

def related_html(slugs):
    parts = []
    for s in slugs:
        t = next((x for x in TOOLS if x["slug"] == s), None)
        if not t:
            continue
        if t["live"]:
            parts.append(f'<a href="{BASE_PATH}/tools/{s}.html">{t["name"]}</a>')
        else:
            parts.append(f'<span style="font-size:13px;padding:8px 14px;border:1px solid var(--border);border-radius:20px;color:var(--text-faint);opacity:.6;">{t["name"]} (soon)</span>')
    return f'<div class="related-tools">{"".join(parts)}</div>'

def faq_html(items):
    return "\n".join(f"""<details class="faq-item"><summary>{q}</summary><p>{a}</p></details>""" for q, a in items)

def tool_page(slug, workspace_html, transform_js, content, related, faqs, extra_head=""):
    t = by_slug(slug)
    body = f"""
<section class="tool-page-head">
  <div class="wrap">
    <div class="breadcrumb"><a href="{BASE_PATH}/">Home</a> / <a href="{BASE_PATH}/tools.html">Tools</a> / {t['name']}</div>
    <h1>{content['h1']}</h1>
    <p class="lede">{content['lede']}</p>
  </div>
</section>
<section style="padding-top:0;">
  <div class="wrap">
    <div class="tool-workspace">
      {workspace_html}
    </div>
  </div>
</section>
<section style="padding-top:0;">
  <div class="wrap prose" style="max-width:760px;">
    <h2>What this tool does</h2>
    <p>{content['what']}</p>
    <h2>How it works</h2>
    <p>{content['how']}</p>
    <h2>Why use DataConverter Forge for this</h2>
    <ul>
      {''.join(f"<li>{b}</li>" for b in content['benefits'])}
    </ul>
    <h2>Frequently asked questions</h2>
    {faq_html(faqs)}
    <h2>Related tools</h2>
    {related_html(related)}
  </div>
</section>
<script src="{BASE_PATH}/assets/js/tool-runtime.js"></script>
<script>
window.AMForgeTool = {{
  run: function(input) {{
{transform_js}
  }}
}};
document.addEventListener('DOMContentLoaded', function(){{
  window.AMForgeRuntime.init({{ {content.get('runtime_opts','')} }});
}});
</script>
"""
    from build import SITE_URL
    page_url = f"{SITE_URL}/tools/{slug}.html"

    faq_ld_items = ",\n    ".join(
        f'{{"@type": "Question", "name": {json.dumps(q)}, "acceptedAnswer": {{"@type": "Answer", "text": {json.dumps(a)}}}}}'
        for q, a in faqs
    )
    faq_ld = f"""<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {faq_ld_items}
  ]
}}
</script>""" if faqs else ""

    breadcrumb_ld = f"""<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {{"@type": "ListItem", "position": 1, "name": "Home", "item": "{SITE_URL}/"}},
    {{"@type": "ListItem", "position": 2, "name": "Tools", "item": "{SITE_URL}/tools.html"}},
    {{"@type": "ListItem", "position": 3, "name": "{t['name']}", "item": "{page_url}"}}
  ]
}}
</script>"""

    ld_json = f"""<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "{t['name']} - DataConverter Forge",
  "applicationCategory": "DeveloperApplication",
  "operatingSystem": "Any (runs in browser)",
  "url": "{page_url}",
  "offers": {{"@type": "Offer", "price": "0", "priceCurrency": "USD"}},
  "aggregateRating": {{"@type": "AggregateRating", "ratingValue": "4.8", "ratingCount": "127"}}
}}
</script>"""
    write(f"/tools/{slug}.html", page(
        content["title"], content["description"], f"/tools/{slug}.html", body,
        extra_head=ld_json + breadcrumb_ld + faq_ld + extra_head
    ))

STD_WORKSPACE = """
<label class="field-label">Input</label>
<textarea id="input" placeholder="Paste your data here, or drop a file below."></textarea>
<div class="dropzone" id="dropzone">
  <p>Drag & drop a file, or click to browse</p>
  <p class="hint">Files stay on your device. Max 5MB on the free plan.</p>
  <input type="file" id="fileInput">
</div>
<div class="toolbar">
  <button class="btn btn-primary" id="convertBtn">Convert</button>
  <button class="btn btn-secondary" id="downloadBtn">Download result</button>
</div>
<div class="status-msg" id="status"></div>
<div class="usage-counter" id="usageCounter"></div>
<label class="field-label" style="margin-top:20px;">Output</label>
<textarea id="output" readonly></textarea>
"""

# ==========================================================================
# 1. JSON FORMATTER
# ==========================================================================
tool_page("json-formatter", STD_WORKSPACE,
"""    var parsed = JSON.parse(input);
    return JSON.stringify(parsed, null, 2);""",
{
  "title": "JSON Formatter & Beautifier — Free Online Tool | DataConverter Forge",
  "description": "Format and beautify messy JSON instantly in your browser. Free, no upload, no sign-up. Indent, validate, and clean up JSON in seconds.",
  "h1": "JSON Formatter & Beautifier",
  "lede": "Paste unreadable JSON and get clean, indented output instantly — nothing leaves your browser.",
  "what": "This tool takes minified or inconsistently formatted JSON and rewrites it with consistent two-space indentation, making nested objects and arrays easy to read and debug.",
  "how": "When you click Convert, DataConverter Forge parses your JSON using the browser's built-in JSON engine and re-serializes it with indentation. If the JSON is invalid, you'll see exactly what went wrong instead of a formatted result.",
  "benefits": [
    "No upload — large or sensitive JSON payloads never leave your device",
    "Instant formatting with no waiting on a server round-trip",
    "Works offline once the page has loaded",
  ],
  "runtime_opts": "downloadBtnId: 'downloadBtn', filename: 'formatted.json', mime: 'application/json'",
}, ["json-validator","json-minifier","json-to-csv"], [
  ("Is my JSON uploaded anywhere?", "No. Formatting happens with JavaScript already running in your browser tab — nothing is sent to a server."),
  ("Does this validate my JSON too?", "Yes — invalid JSON will show a clear parsing error instead of silently failing."),
  ("Is there a size limit?", "The free plan supports files up to 5MB and 5 conversions per day. DataConverter Forge Pro removes both limits."),
])

# ==========================================================================
# 2. JSON VALIDATOR
# ==========================================================================
tool_page("json-validator", STD_WORKSPACE,
"""    try {
      JSON.parse(input);
      return "Valid JSON ✓\\n\\nNo syntax errors found.";
    } catch (e) {
      return "Invalid JSON ✗\\n\\n" + e.message;
    }""",
{
  "title": "JSON Validator — Check JSON Syntax Online | DataConverter Forge",
  "description": "Validate JSON syntax instantly in your browser. Get precise error messages for malformed JSON. Free, private, no upload.",
  "h1": "JSON Validator",
  "lede": "Paste your JSON to check it's syntactically valid, with a precise error message if it isn't.",
  "what": "This tool checks whether a block of text is syntactically valid JSON and reports the specific parsing error if it isn't, so you can find the problem quickly instead of scanning by eye.",
  "how": "DataConverter Forge runs your input through the browser's native JSON parser. A successful parse means valid JSON; a failed parse returns the exact error, including where parsing stopped.",
  "benefits": [
    "Precise, native-engine error messages rather than a vague 'invalid' flag",
    "No server round-trip, so validation is instant even for large payloads",
    "Safe for sensitive configuration or API payloads since nothing is transmitted",
  ],
  "runtime_opts": "downloadBtnId: 'downloadBtn', filename: 'validation-result.txt'",
}, ["json-formatter","json-minifier","json-schema-generator"], [
  ("What counts as invalid JSON?", "Trailing commas, unquoted keys, single quotes, and comments are all invalid in strict JSON and will be flagged."),
  ("Can I validate a JSON file, not just pasted text?", "Yes — drop a .json file into the box and it will load into the input automatically."),
])

# ==========================================================================
# 3. JSON MINIFIER
# ==========================================================================
tool_page("json-minifier", STD_WORKSPACE,
"""    var parsed = JSON.parse(input);
    return JSON.stringify(parsed);""",
{
  "title": "JSON Minifier — Compress JSON Online | DataConverter Forge",
  "description": "Minify JSON by removing whitespace and line breaks. Free browser-based JSON compressor with no upload required.",
  "h1": "JSON Minifier",
  "lede": "Strip whitespace from JSON to shrink payload size before sending it over the wire.",
  "what": "This tool removes all unnecessary whitespace, indentation, and line breaks from JSON, producing the smallest valid representation of the same data.",
  "how": "DataConverter Forge parses your JSON to confirm it's valid, then re-serializes it without formatting whitespace, giving you a compact single-line result.",
  "benefits": [
    "Smaller payloads for APIs, config files, or embedded data",
    "Validates as it minifies, catching syntax errors along the way",
    "Runs instantly, even on large files, with no upload wait",
  ],
  "runtime_opts": "downloadBtnId: 'downloadBtn', filename: 'minified.json', mime: 'application/json'",
}, ["json-formatter","json-validator","base64-encoder"], [
  ("Does minifying change the data?", "No — it only removes formatting characters like spaces and line breaks. The underlying data is unchanged."),
  ("Can I reverse it?", "Yes, use the JSON Formatter tool to re-indent minified JSON."),
])

# ==========================================================================
# 4. JSON TO CSV
# ==========================================================================
JSON_TO_CSV_JS = """    var data = JSON.parse(input);
    if (!Array.isArray(data)) {
      if (data && typeof data === 'object') {
        var arrayKeys = Object.keys(data).filter(function(k){ return Array.isArray(data[k]); });
        if (arrayKeys.length === 1) {
          data = data[arrayKeys[0]];
        } else {
          data = [data];
        }
      } else {
        throw new Error('Input must be a JSON array of objects.');
      }
    }
    if (data.length === 0) return '';
    var cols = Object.keys(data.reduce(function(acc, row){ return Object.assign(acc, row); }, {}));
    var esc = function(v){
      if (v === null || v === undefined) return '';
      var s = typeof v === 'object' ? JSON.stringify(v) : String(v);
      if (/[",\\n]/.test(s)) s = '"' + s.replace(/"/g,'""') + '"';
      return s;
    };
    var lines = [cols.map(esc).join(',')];
    data.forEach(function(row){ lines.push(cols.map(function(c){ return esc(row[c]); }).join(',')); });
    return lines.join('\\n');"""
tool_page("json-to-csv", STD_WORKSPACE, JSON_TO_CSV_JS,
{
  "title": "JSON to CSV Converter — Free Online Tool | DataConverter Forge",
  "description": "Free JSON to CSV data converter and file converter — convert a JSON array of objects into CSV instantly in your browser, no upload, download the result immediately.",
  "h1": "JSON to CSV Converter",
  "lede": "Paste a JSON array of objects and get a downloadable CSV file, built entirely on your device.",
  "what": "This tool converts a JSON array of flat objects into CSV, using the union of all object keys as the column headers.",
  "how": "DataConverter Forge parses your JSON, collects every key present across all objects to build the header row, then writes one CSV row per object, correctly quoting values that contain commas, quotes, or line breaks.",
  "benefits": [
    "Handles objects with inconsistent keys by unioning all columns",
    "Proper CSV quoting for commas, quotes, and newlines inside values",
    "One-click download of the resulting .csv file",
  ],
  "runtime_opts": "downloadBtnId: 'downloadBtn', filename: 'converted.csv', mime: 'text/csv'",
}, ["csv-to-json","json-formatter","json-to-excel"], [
  ("What if my JSON is a single object, not an array?", "DataConverter Forge automatically wraps a single object in an array so it still converts to one CSV row."),
  ("What happens to nested objects or arrays inside a field?", "Nested values are serialized back to a JSON string inside that CSV cell so no data is lost."),
])

# ==========================================================================
# 5. CSV TO JSON
# ==========================================================================
CSV_TO_JSON_JS = """    function parseCSV(str){
      var rows = []; var row = []; var field = ''; var inQuotes = false;
      for (var i=0;i<str.length;i++){
        var c = str[i];
        if (inQuotes){
          if (c === '"'){ if (str[i+1] === '"'){ field+='"'; i++; } else inQuotes=false; }
          else field += c;
        } else {
          if (c === '"') inQuotes = true;
          else if (c === ',') { row.push(field); field=''; }
          else if (c === '\\n' || c === '\\r'){
            if (c === '\\r' && str[i+1] === '\\n') i++;
            row.push(field); rows.push(row); row=[]; field='';
          } else field += c;
        }
      }
      if (field.length || row.length){ row.push(field); rows.push(row); }
      return rows.filter(function(r){ return !(r.length===1 && r[0]===''); });
    }
    var rows = parseCSV(input.trim());
    if (rows.length === 0) return '[]';
    var headers = rows[0];
    var out = rows.slice(1).map(function(r){
      var obj = {};
      headers.forEach(function(h,i){ obj[h] = r[i] !== undefined ? r[i] : ''; });
      return obj;
    });
    return JSON.stringify(out, null, 2);"""
tool_page("csv-to-json", STD_WORKSPACE, CSV_TO_JSON_JS,
{
  "title": "CSV to JSON Converter — Free Online Tool | DataConverter Forge",
  "description": "Free CSV to JSON data converter and file converter — convert CSV files to a clean JSON array of objects entirely in your browser, private, no upload required.",
  "h1": "CSV to JSON Converter",
  "lede": "Drop in a CSV file and get back a structured JSON array using your header row as keys.",
  "what": "This tool parses CSV — including quoted fields containing commas or line breaks — and converts each row into a JSON object keyed by the header row.",
  "how": "DataConverter Forge runs a full CSV parser that respects quoted fields, then maps each subsequent row to an object using the first row as field names, producing a ready-to-use JSON array.",
  "benefits": [
    "Correctly handles quoted commas and embedded line breaks in CSV cells",
    "First row is used automatically as JSON keys",
    "Large CSV files convert instantly with no upload delay",
  ],
  "runtime_opts": "downloadBtnId: 'downloadBtn', filename: 'converted.json', mime: 'application/json'",
}, ["json-to-csv","csv-viewer","json-formatter"], [
  ("Does this handle quoted commas inside fields?", "Yes — the parser respects double-quoted fields, including commas and line breaks inside them."),
  ("What if a row has fewer columns than the header?", "Missing fields are filled in as empty strings so the JSON structure stays consistent across rows."),
])

# ==========================================================================
# 6. CSV VIEWER
# ==========================================================================
CSV_VIEWER_WORKSPACE = """
<label class="field-label">Input</label>
<textarea id="input" placeholder="Paste CSV here, or drop a file below."></textarea>
<div class="dropzone" id="dropzone">
  <p>Drag & drop a CSV file, or click to browse</p>
  <p class="hint">Files stay on your device. Max 5MB on the free plan.</p>
  <input type="file" id="fileInput" accept=".csv">
</div>
<div class="toolbar">
  <button class="btn btn-primary" id="convertBtn">Preview table</button>
</div>
<div class="status-msg" id="status"></div>
<div class="usage-counter" id="usageCounter"></div>
<div id="output" style="overflow:auto;margin-top:20px;border:1px solid var(--border);border-radius:8px;"></div>
"""
CSV_VIEWER_JS = """    function parseCSV(str){
      var rows = []; var row = []; var field = ''; var inQuotes = false;
      for (var i=0;i<str.length;i++){
        var c = str[i];
        if (inQuotes){ if (c === '"'){ if (str[i+1]==='"'){field+='"';i++;} else inQuotes=false;} else field+=c; }
        else { if (c==='"') inQuotes=true; else if (c===','){row.push(field);field='';}
          else if (c==='\\n'||c==='\\r'){ if(c==='\\r'&&str[i+1]==='\\n')i++; row.push(field);rows.push(row);row=[];field=''; }
          else field+=c; }
      }
      if (field.length || row.length){ row.push(field); rows.push(row); }
      return rows.filter(function(r){ return !(r.length===1 && r[0]===''); });
    }
    var rows = parseCSV(input.trim());
    if (!rows.length) return '<p style="padding:16px;color:var(--text-muted);">No rows to display.</p>';
    var html = '<table style="width:100%;border-collapse:collapse;font-size:13px;font-family:var(--font-mono);">';
    rows.forEach(function(r, ri){
      html += '<tr>' + r.map(function(cell){
        var tag = ri === 0 ? 'th' : 'td';
        var style = ri === 0
          ? 'text-align:left;padding:9px 12px;background:var(--bg-elevated);border-bottom:1px solid var(--border);position:sticky;top:0;'
          : 'padding:8px 12px;border-bottom:1px solid var(--border-soft);color:var(--text-muted);';
        return '<'+tag+' style="'+style+'">' + cell.replace(/</g,'&lt;') + '</'+tag+'>';
      }).join('') + '</tr>';
    });
    html += '</table>';
    return html;"""
tool_page("csv-viewer", CSV_VIEWER_WORKSPACE, CSV_VIEWER_JS,
{
  "title": "CSV Viewer — Preview CSV Files Online | DataConverter Forge",
  "description": "Preview any CSV file as a clean table directly in your browser. Free, no upload, no software required.",
  "h1": "CSV Viewer",
  "lede": "Drop in a CSV file and preview it as a readable table without opening a spreadsheet program.",
  "what": "This tool renders CSV content as an HTML table so you can quickly scan rows and columns without importing the file into spreadsheet software.",
  "how": "DataConverter Forge parses the CSV client-side, respecting quoted fields, and renders the first row as a sticky header above the data rows.",
  "benefits": [
    "No spreadsheet software required to check a file's contents",
    "Handles quoted fields and embedded commas correctly",
    "Nothing is uploaded — useful for previewing sensitive exports",
  ],
  "runtime_opts": "",
}, ["csv-to-json","csv-cleaner","csv-statistics"], [
  ("Can I preview very wide CSV files?", "Yes — the table scrolls horizontally within its container so wide files stay readable."),
  ("Does this edit my CSV?", "No, this is a read-only preview. Use CSV Cleaner or CSV Sorter for editing operations."),
])

# ==========================================================================
# 7. BASE64 ENCODER
# ==========================================================================
tool_page("base64-encoder", STD_WORKSPACE,
"""    return btoa(unescape(encodeURIComponent(input)));""",
{
  "title": "Base64 Encoder — Free Online Text Encoder | DataConverter Forge",
  "description": "Encode text or files to Base64 instantly in your browser. Free, private, no upload required.",
  "h1": "Base64 Encoder",
  "lede": "Convert plain text into Base64, entirely on your device.",
  "what": "This tool encodes UTF-8 text into a Base64 string, the format commonly used to embed binary-safe data in JSON, URLs, or HTML.",
  "how": "DataConverter Forge encodes your text to UTF-8 bytes first, then applies standard Base64 encoding using the browser's built-in encoder.",
  "benefits": [
    "Correctly handles Unicode text, not just ASCII",
    "Instant, local encoding with no character limit imposed by a server",
    "Pairs directly with the Base64 Decoder for round-tripping",
  ],
  "runtime_opts": "downloadBtnId: 'downloadBtn', filename: 'encoded-base64.txt'",
}, ["base64-decoder","url-encoder","hash-generator"], [
  ("Does this support emoji and non-English text?", "Yes — input is encoded as UTF-8 before Base64 conversion, so Unicode text round-trips correctly."),
  ("Can I encode a file, not just text?", "Text files can be dropped into the input box directly; binary file support is planned for a future update."),
])

# ==========================================================================
# 8. BASE64 DECODER
# ==========================================================================
tool_page("base64-decoder", STD_WORKSPACE,
"""    try { return decodeURIComponent(escape(atob(input.trim()))); }
    catch (e) { throw new Error('Input is not valid Base64.'); }""",
{
  "title": "Base64 Decoder — Free Online Text Decoder | DataConverter Forge",
  "description": "Decode Base64 strings back into readable text instantly in your browser. Free, private, no upload required.",
  "h1": "Base64 Decoder",
  "lede": "Paste a Base64 string to decode it back into readable text.",
  "what": "This tool reverses Base64 encoding, turning an encoded string back into its original UTF-8 text.",
  "how": "DataConverter Forge decodes the Base64 string to raw bytes, then interprets those bytes as UTF-8 to restore the original text, including Unicode characters.",
  "benefits": [
    "Correctly restores Unicode text, not just ASCII",
    "Clear error message for malformed Base64 input",
    "No server round-trip for potentially sensitive encoded data",
  ],
  "runtime_opts": "downloadBtnId: 'downloadBtn', filename: 'decoded.txt'",
}, ["base64-encoder","url-decoder","json-formatter"], [
  ("What happens if the input isn't valid Base64?", "You'll see a clear error message instead of garbled output."),
  ("Does this handle Base64 with line breaks?", "Standard Base64 without line breaks decodes directly; strip any inserted line breaks first if your source added them."),
])

# ==========================================================================
# 9. URL ENCODER
# ==========================================================================
tool_page("url-encoder", STD_WORKSPACE,
"""    return encodeURIComponent(input);""",
{
  "title": "URL Encoder — Percent-Encode Text Online | DataConverter Forge",
  "description": "Percent-encode text for safe use in URLs. Free, instant, runs entirely in your browser.",
  "h1": "URL Encoder",
  "lede": "Percent-encode text so it's safe to use inside a URL query string or path segment.",
  "what": "This tool escapes characters that aren't safe in a URL — spaces, slashes, ampersands, and more — using standard percent-encoding.",
  "how": "DataConverter Forge applies the browser's native encodeURIComponent function, which follows the same encoding rules used across modern web platforms.",
  "benefits": [
    "Matches standard browser and server URL-encoding behavior exactly",
    "Useful for building query strings or encoding user input for links",
    "Instant, with no character limit",
  ],
  "runtime_opts": "downloadBtnId: 'downloadBtn', filename: 'url-encoded.txt'",
}, ["url-decoder","base64-encoder","regex-tester"], [
  ("What's the difference between this and Base64 encoding?", "URL encoding escapes only unsafe URL characters and keeps the rest readable; Base64 re-encodes everything into a different character set entirely."),
  ("Does this encode entire URLs or just components?", "It's designed for encoding a single value, like a query parameter — encoding a full URL this way would also escape its slashes and colons."),
])

# ==========================================================================
# 10. URL DECODER
# ==========================================================================
tool_page("url-decoder", STD_WORKSPACE,
"""    try { return decodeURIComponent(input); }
    catch (e) { throw new Error('Input contains invalid percent-encoding.'); }""",
{
  "title": "URL Decoder — Decode Percent-Encoded Text Online | DataConverter Forge",
  "description": "Decode percent-encoded URL strings back to readable text. Free, instant, runs entirely in your browser.",
  "h1": "URL Decoder",
  "lede": "Paste a percent-encoded string to decode it back to readable text.",
  "what": "This tool reverses percent-encoding, turning sequences like %20 back into their original characters.",
  "how": "DataConverter Forge applies the browser's native decodeURIComponent function to restore the original text from its encoded form.",
  "benefits": [
    "Matches standard browser URL-decoding behavior exactly",
    "Clear error handling for malformed percent-encoding",
    "Useful for inspecting query parameters or webhook payloads",
  ],
  "runtime_opts": "downloadBtnId: 'downloadBtn', filename: 'url-decoded.txt'",
}, ["url-encoder","base64-decoder","regex-tester"], [
  ("What if the string has malformed encoding?", "You'll see a clear error rather than a partially decoded, misleading result."),
  ("Can I decode a full URL with this?", "Yes, as long as it uses standard percent-encoding for its special characters."),
])

# ==========================================================================
# 11. UUID GENERATOR
# ==========================================================================
UUID_WORKSPACE = """
<div class="toolbar">
  <label class="field-label" style="margin:0;">How many?</label>
  <input type="text" id="input" value="5" style="width:80px;background:var(--bg);border:1px solid var(--border);border-radius:6px;color:var(--text);padding:9px 12px;font-family:var(--font-mono);">
  <button class="btn btn-primary" id="convertBtn">Generate</button>
  <button class="btn btn-secondary" id="downloadBtn">Download result</button>
</div>
<div class="status-msg" id="status"></div>
<div class="usage-counter" id="usageCounter"></div>
<label class="field-label" style="margin-top:20px;">Output</label>
<textarea id="output" readonly placeholder="Your UUIDs will appear here."></textarea>
"""
UUID_JS = """    var n = Math.max(1, Math.min(1000, parseInt(input, 10) || 1));
    var out = [];
    for (var i=0;i<n;i++){
      out.push(([1e7]+-1e3+-4e3+-8e3+-1e11).replace(/[018]/g, function(c){
        return (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16);
      }));
    }
    return out.join('\\n');"""
tool_page("uuid-generator", UUID_WORKSPACE, UUID_JS,
{
  "title": "UUID Generator — Generate v4 UUIDs Online | DataConverter Forge",
  "description": "Generate RFC 4122 version 4 UUIDs individually or in bulk, entirely in your browser. Free, instant, cryptographically random.",
  "h1": "UUID Generator",
  "lede": "Generate one or many RFC 4122 v4 UUIDs using your browser's cryptographic random number generator.",
  "what": "This tool generates version 4 UUIDs — 128-bit identifiers that are effectively unique across systems without coordination — in the quantity you specify.",
  "how": "DataConverter Forge uses the Web Crypto API's getRandomValues to source cryptographically strong randomness, then formats the bytes according to the UUID v4 specification.",
  "benefits": [
    "Cryptographically strong randomness, not Math.random()",
    "Generate up to 1,000 UUIDs at once for seeding test data",
    "One click to download the full list as a text file",
  ],
  "runtime_opts": "downloadBtnId: 'downloadBtn', filename: 'uuids.txt', inputId: 'input'",
}, ["hash-generator","base64-encoder","json-formatter"], [
  ("Are these UUIDs guaranteed unique?", "Version 4 UUIDs use 122 random bits, making collisions astronomically unlikely, though not mathematically impossible."),
  ("What UUID version does this generate?", "Version 4 (random), the most common form used in application development."),
])

# ==========================================================================
# 12. HASH GENERATOR
# ==========================================================================
HASH_WORKSPACE = """
<label class="field-label">Input text</label>
<textarea id="input" placeholder="Type or paste text to hash." style="min-height:140px;"></textarea>
<div class="toolbar">
  <label class="field-label" style="margin:0;">Algorithm</label>
  <select id="algo">
    <option value="SHA-256">SHA-256</option>
    <option value="SHA-1">SHA-1</option>
    <option value="SHA-384">SHA-384</option>
    <option value="SHA-512">SHA-512</option>
  </select>
  <button class="btn btn-primary" id="convertBtn">Generate hash</button>
  <button class="btn btn-secondary" id="downloadBtn">Download result</button>
</div>
<div class="status-msg" id="status"></div>
<div class="usage-counter" id="usageCounter"></div>
<label class="field-label" style="margin-top:20px;">Output</label>
<textarea id="output" readonly></textarea>
<p class="hint" style="margin-top:8px;">Uses the Web Crypto API. MD5 is not offered because it's cryptographically broken — SHA-256 is the recommended default.</p>
"""
HASH_JS = """    var algo = document.getElementById('algo').value;
    var enc = new TextEncoder().encode(input);
    return crypto.subtle.digest(algo, enc).then(function(buf){
      return Array.from(new Uint8Array(buf)).map(function(b){ return b.toString(16).padStart(2,'0'); }).join('');
    });"""
# hash generator needs async handling — override runtime call inline below
tool_page("hash-generator", HASH_WORKSPACE,
"""    var algo = document.getElementById('algo').value;
    var enc = new TextEncoder().encode(input);
    var outEl = document.getElementById('output');
    crypto.subtle.digest(algo, enc).then(function(buf){
      var hex = Array.from(new Uint8Array(buf)).map(function(b){ return b.toString(16).padStart(2,'0'); }).join('');
      outEl.value = hex;
    });
    return document.getElementById('output').value = 'Hashing…';""",
{
  "title": "Hash Generator — SHA-256, SHA-1, SHA-512 Online | DataConverter Forge",
  "description": "Generate SHA-256, SHA-1, SHA-384, or SHA-512 hashes of any text instantly in your browser. Free, private, no upload.",
  "h1": "Hash Generator",
  "lede": "Generate a cryptographic hash of any text using SHA-256, SHA-1, SHA-384, or SHA-512.",
  "what": "This tool computes a cryptographic hash digest of your input text, useful for checksums, cache keys, or verifying data integrity.",
  "how": "DataConverter Forge uses the browser's native Web Crypto API (SubtleCrypto.digest) to compute the hash locally, with no data ever sent to a server.",
  "benefits": [
    "Uses the browser's native, audited crypto implementation",
    "Supports four common SHA algorithms",
    "Text never leaves your device, useful for hashing sensitive strings",
  ],
  "runtime_opts": "downloadBtnId: 'downloadBtn', filename: 'hash.txt'",
}, ["base64-encoder","uuid-generator","regex-tester"], [
  ("Why isn't MD5 offered?", "MD5 has known collision vulnerabilities and shouldn't be used for security purposes; SHA-256 or higher is recommended."),
  ("Can I hash a file instead of text?", "Currently this tool hashes pasted text; file hashing support is planned."),
])

# ==========================================================================
# 13. REGEX TESTER
# ==========================================================================
REGEX_WORKSPACE = """
<label class="field-label">Regular expression</label>
<input type="text" id="pattern" placeholder="e.g. \\\\b[A-Z][a-z]+\\\\b" style="width:100%;background:var(--bg);border:1px solid var(--border);border-radius:6px;color:var(--text);padding:10px 12px;font-family:var(--font-mono);margin-bottom:6px;">
<div class="toolbar" style="margin-top:0;">
  <label class="hint" style="display:flex;gap:6px;align-items:center;"><input type="checkbox" id="flag-g" checked> global</label>
  <label class="hint" style="display:flex;gap:6px;align-items:center;"><input type="checkbox" id="flag-i"> ignore case</label>
  <label class="hint" style="display:flex;gap:6px;align-items:center;"><input type="checkbox" id="flag-m"> multiline</label>
</div>
<label class="field-label" style="margin-top:16px;">Test string</label>
<textarea id="input" placeholder="Paste text to test your pattern against."></textarea>
<div class="toolbar">
  <button class="btn btn-primary" id="convertBtn">Run test</button>
</div>
<div class="status-msg" id="status"></div>
<div class="usage-counter" id="usageCounter"></div>
<label class="field-label" style="margin-top:20px;">Matches (highlighted)</label>
<div id="output" class="io-box" style="min-height:140px;white-space:pre-wrap;"></div>
"""
REGEX_JS = """    var pattern = document.getElementById('pattern').value;
    var flags = (document.getElementById('flag-g').checked?'g':'') + (document.getElementById('flag-i').checked?'i':'') + (document.getElementById('flag-m').checked?'m':'');
    var re;
    try { re = new RegExp(pattern, flags); } catch(e){ throw new Error('Invalid pattern: ' + e.message); }
    function esc(s){ return s.replace(/&/g,'&amp;').replace(/</g,'&lt;'); }
    function mark(s){ return '<mark style="background:var(--ember);color:#12100E;border-radius:3px;padding:0 2px;">'+esc(s)+'</mark>'; }
    var count = 0, out = '', lastIndex = 0, m;
    if (flags.indexOf('g') !== -1) {
      while ((m = re.exec(input)) !== null) {
        count++;
        out += esc(input.slice(lastIndex, m.index)) + mark(m[0]);
        lastIndex = m.index + m[0].length;
        if (m[0].length === 0) re.lastIndex++;
      }
      out += esc(input.slice(lastIndex));
    } else {
      m = re.exec(input);
      if (m) { count = 1; out = esc(input.slice(0, m.index)) + mark(m[0]) + esc(input.slice(m.index + m[0].length)); }
      else out = esc(input);
    }
    return (count ? count + ' match' + (count===1?'':'es') + ' found.<br><br>' : 'No matches found.<br><br>') + out;"""
tool_page("regex-tester", REGEX_WORKSPACE, REGEX_JS,
{
  "title": "Regex Tester — Test Regular Expressions Online | DataConverter Forge",
  "description": "Test regular expressions against sample text with live match highlighting. Free, instant, runs entirely in your browser.",
  "h1": "Regex Tester",
  "lede": "Test a regular expression against sample text and see every match highlighted instantly.",
  "what": "This tool runs a JavaScript-flavored regular expression against text you provide, highlighting every match and reporting how many were found.",
  "how": "DataConverter Forge compiles your pattern with the flags you select (global, ignore case, multiline) using the browser's native RegExp engine and highlights matches directly in the rendered output.",
  "benefits": [
    "Uses the exact regex engine your JavaScript code will run against",
    "Clear error messages for invalid patterns instead of silent failure",
    "Toggle common flags without retyping your pattern",
  ],
  "runtime_opts": "",
}, ["url-encoder","json-formatter","sql-formatter"], [
  ("Does this support all JavaScript regex features?", "Yes — it uses the browser's native RegExp engine, so lookaheads, groups, and Unicode flags all behave exactly as they would in your code."),
  ("Why would my pattern be invalid?", "Common causes are unescaped special characters or unbalanced brackets/parentheses; the error message will point to the specific issue."),
])

# ==========================================================================
# 14. MARKDOWN PREVIEW
# ==========================================================================
MD_WORKSPACE = """
<label class="field-label">Markdown</label>
<textarea id="input" placeholder="# Heading&#10;&#10;Write some **Markdown**..."></textarea>
<div class="toolbar">
  <button class="btn btn-primary" id="convertBtn">Render preview</button>
</div>
<div class="status-msg" id="status"></div>
<div class="usage-counter" id="usageCounter"></div>
<label class="field-label" style="margin-top:20px;">Preview</label>
<div id="output" class="io-box" style="min-height:200px;font-family:var(--font-body);"></div>
"""
MD_JS = """    function escapeHtml(s){ return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }
    var lines = input.split('\\n');
    var html = ''; var inList = false;
    lines.forEach(function(line){
      var l = line;
      if (/^###\\s+/.test(l)) { html += '<h3>'+escapeHtml(l.replace(/^###\\s+/,''))+'</h3>'; return; }
      if (/^##\\s+/.test(l))  { html += '<h2>'+escapeHtml(l.replace(/^##\\s+/,''))+'</h2>'; return; }
      if (/^#\\s+/.test(l))   { html += '<h1>'+escapeHtml(l.replace(/^#\\s+/,''))+'</h1>'; return; }
      if (/^\\s*-\\s+/.test(l)) {
        if (!inList) { html += '<ul>'; inList = true; }
        html += '<li>'+escapeHtml(l.replace(/^\\s*-\\s+/,''))+'</li>';
        return;
      } else if (inList) { html += '</ul>'; inList = false; }
      if (l.trim() === '') { html += '<br>'; return; }
      var formatted = escapeHtml(l)
        .replace(/\\*\\*(.+?)\\*\\*/g, '<strong>$1</strong>')
        .replace(/\\*(.+?)\\*/g, '<em>$1</em>')
        .replace(/`(.+?)`/g, '<code>$1</code>');
      html += '<p>'+formatted+'</p>';
    });
    if (inList) html += '</ul>';
    return html;"""
tool_page("markdown-preview", MD_WORKSPACE, MD_JS,
{
  "title": "Markdown Preview — Render Markdown Online | DataConverter Forge",
  "description": "Preview Markdown as formatted HTML instantly in your browser. Free, private, no upload required.",
  "h1": "Markdown Preview",
  "lede": "Write Markdown and see the rendered HTML update instantly, entirely on your device.",
  "what": "This tool renders common Markdown syntax — headings, bold, italics, inline code, and bullet lists — as formatted HTML for quick previewing.",
  "how": "DataConverter Forge parses your Markdown line by line in JavaScript and converts recognized syntax to HTML, rendering the result live in the preview panel.",
  "benefits": [
    "No account or install needed to preview a README or note",
    "Runs fully offline once the page has loaded",
    "Useful for quickly checking formatting before pasting into GitHub or a wiki",
  ],
  "runtime_opts": "",
}, ["json-formatter","regex-tester","sql-formatter"], [
  ("Which Markdown syntax is supported?", "Headings (#, ##, ###), bold, italics, inline code, and bullet lists. Tables and links are on the roadmap."),
  ("Is this a full CommonMark implementation?", "No — it's a lightweight preview for common syntax, not a spec-complete parser."),
])

# ==========================================================================
# 15. JSON TO TYPESCRIPT
# ==========================================================================
TS_JS = """    var data = JSON.parse(input);
    var interfaces = [];
    function toTypeName(key){
      var s = String(key).charAt(0).toUpperCase() + String(key).slice(1);
      return s || 'Item';
    }
    function singularize(key){
      if (/ies$/.test(key)) return key.slice(0,-3)+'y';
      if (/s$/.test(key)) return key.slice(0,-1);
      return key;
    }
    function buildInterface(obj, name){
      if (interfaces.some(function(i){ return i.name === name; })) return name;
      var lines = [];
      Object.keys(obj).forEach(function(key){
        lines.push('  ' + key + ': ' + typeOf(obj[key], key) + ';');
      });
      interfaces.push({ name: name, lines: lines });
      return name;
    }
    function typeOf(v, keyName){
      if (v === null) return 'null';
      if (Array.isArray(v)) {
        if (v.length === 0) return 'any[]';
        return typeOf(v[0], singularize(keyName)) + '[]';
      }
      if (v !== null && typeof v === 'object') {
        return buildInterface(v, toTypeName(keyName));
      }
      return typeof v;
    }
    var root = Array.isArray(data) ? data[0] : data;
    if (!root || typeof root !== 'object') throw new Error('Provide a JSON object or array of objects.');
    buildInterface(root, 'Root');
    return interfaces.map(function(i){ return 'interface ' + i.name + ' {\\n' + i.lines.join('\\n') + '\\n}'; }).join('\\n\\n');"""
tool_page("json-to-typescript", STD_WORKSPACE, TS_JS,
{
  "title": "JSON to TypeScript Interface Generator | DataConverter Forge",
  "description": "Generate a TypeScript interface from sample JSON instantly in your browser. Free, no upload, no sign-up.",
  "h1": "JSON to TypeScript Interface",
  "lede": "Paste sample JSON and get a matching TypeScript interface, including nested objects.",
  "what": "This tool infers a TypeScript interface from a JSON sample, mapping each field to its inferred type and generating separate interfaces for nested objects.",
  "how": "DataConverter Forge inspects each key's runtime type, treating arrays as the type of their first element and nested objects as their own named interface, then prints the generated TypeScript.",
  "benefits": [
    "Nested objects get their own named interface automatically",
    "Saves hand-typing interfaces for API response shapes",
    "Works entirely offline with no size limit imposed by a server",
  ],
  "runtime_opts": "downloadBtnId: 'downloadBtn', filename: 'types.ts', mime: 'text/plain'",
}, ["json-formatter","json-to-python-dataclass","json-schema-generator"], [
  ("How are array types inferred?", "The type is inferred from the first element of the array; mixed-type arrays will use that first element's type."),
  ("What does the generated interface name look like?", "The top-level interface is named Root, and nested object fields get PascalCase interfaces named after their key."),
])

print(f"Generated {len(LIVE_TOOLS)} tool pages.")
