"""HTML rendering for the package index site.

This module owns presentation only: given plain data (title, description,
rows, usage blocks, ...) it returns a full HTML document as a string. It
does not touch the filesystem and does not know about directory scanning.
"""

from __future__ import annotations

import json
from html import escape

# highlight.js is loaded from cdnjs for syntax-highlighted usage snippets.
# "groovy" isn't in the default bundle, so it's pulled in as an extra file;
# bash is already part of the default ~40-language bundle.
HLJS_VERSION = "11.9.0"
HLJS_CSS_URL = f"https://cdnjs.cloudflare.com/ajax/libs/highlight.js/{HLJS_VERSION}/styles/atom-one-dark.min.css"
HLJS_JS_URL = f"https://cdnjs.cloudflare.com/ajax/libs/highlight.js/{HLJS_VERSION}/highlight.min.js"
HLJS_GROOVY_URL = f"https://cdnjs.cloudflare.com/ajax/libs/highlight.js/{HLJS_VERSION}/languages/groovy.min.js"

# Small accent per language so each block's badge reads at a glance.
LANG_BADGE_COLORS = {
    "bash": "#78e398",
    "groovy": "#e0af68",
    "ini": "#7aa2f7",
}
DEFAULT_BADGE_COLOR = "#8f8f8f"

PAGE_CSS = """
:root {
  color-scheme: dark;
  --bg: #0f0f0f;
  --panel: #151515;
  --panel-2: #1b1b1b;
  --text: #e8e8e8;
  --muted: #8f8f8f;
  --line: #2a2a2a;
  --accent: #78e398;
  --accent-soft: rgba(120, 227, 152, 0.12);
}

* { box-sizing: border-box; }

body {
  margin: 0;
  background: var(--bg);
  color: var(--text);
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace;
  font-size: 15px;
  line-height: 1.6;
}

main {
  width: min(960px, calc(100% - 32px));
  margin: 44px auto;
}

header { margin-bottom: 24px; }

h1 {
  margin: 0;
  font-size: clamp(22px, 3.2vw, 32px);
  font-weight: 600;
  letter-spacing: -0.02em;
  line-height: 1.2;
}

.subtitle {
  margin-top: 10px;
  color: var(--muted);
  max-width: 800px;
}

.path {
  display: inline-flex;
  align-items: center;
  margin-top: 16px;
  padding: 6px 10px;
  border: 1px solid var(--line);
  border-radius: 6px;
  background: var(--panel);
  color: var(--accent);
  font-size: 13px;
}

.usage { margin: 20px 0 24px; }

.usage-title {
  margin: 0 0 8px 2px;
  color: var(--muted);
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.code-block {
  margin-bottom: 12px;
  border: 1px solid var(--line);
  border-radius: 10px;
  background: var(--panel);
  overflow: hidden;
}

.code-block:last-child { margin-bottom: 0; }

.code-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 8px 12px;
  border-bottom: 1px solid var(--line);
  background: var(--panel-2);
}

.code-title {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
  color: var(--muted);
  font-size: 13px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.code-lang {
  flex: none;
  padding: 2px 7px;
  border: 1px solid currentColor;
  border-radius: 5px;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.copy-btn {
  flex: none;
  font: inherit;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--muted);
  background: transparent;
  border: 1px solid var(--line);
  border-radius: 6px;
  padding: 3px 10px;
  cursor: pointer;
  transition: color 0.15s ease, border-color 0.15s ease, background 0.15s ease;
}

.copy-btn:hover {
  color: var(--accent);
  border-color: var(--accent);
}

.copy-btn.copied {
  color: var(--accent);
  border-color: var(--accent);
  background: var(--accent-soft);
}

.code-block pre {
  margin: 0;
  padding: 14px;
  overflow-x: auto;
}

.code-block pre code.hljs {
  background: transparent !important;
  padding: 0 !important;
  font-family: inherit;
  font-size: 14px;
}

.table-wrap {
  overflow: hidden;
  border: 1px solid var(--line);
  border-radius: 10px;
  background: var(--panel);
}

table {
  width: 100%;
  border-collapse: collapse;
}

td {
  padding: 11px 14px;
  border-bottom: 1px solid var(--line);
  vertical-align: middle;
}

tr:last-child td { border-bottom: 0; }
tr:hover { background: var(--accent-soft); }

.type {
  width: 130px;
  color: var(--muted);
  text-transform: uppercase;
  font-size: 12px;
  letter-spacing: 0.08em;
}

.name { word-break: break-all; }

.size {
  width: 160px;
  color: var(--muted);
  text-align: right;
  white-space: nowrap;
}

a {
  color: var(--accent);
  text-decoration: none;
}

a:hover { text-decoration: underline; }

footer {
  margin-top: 28px;
  color: var(--muted);
  font-size: 13px;
}

@media (max-width: 640px) {
  main { margin: 28px auto; }
  td { padding: 10px; }
  .type { width: 90px; }
  .size { display: none; }
}
"""

COPY_SCRIPT = """
function copyCode(btn) {
  const block = btn.closest('.code-block');
  const codeEl = block ? block.querySelector('code') : null;
  if (!codeEl) return;

  navigator.clipboard.writeText(codeEl.textContent).then(() => {
    const original = btn.textContent;
    btn.textContent = 'copied';
    btn.classList.add('copied');
    setTimeout(() => {
      btn.textContent = original;
      btn.classList.remove('copied');
    }, 1400);
  }).catch(() => {
    btn.textContent = 'failed';
    setTimeout(() => { btn.textContent = 'copy'; }, 1400);
  });
}

if (window.hljs) {
  hljs.highlightAll();
}
"""


def render_code_block(label: str, lang: str, code: str) -> str:
    badge_color = LANG_BADGE_COLORS.get(lang, DEFAULT_BADGE_COLOR)

    return f"""
      <div class="code-block">
        <div class="code-head">
          <div class="code-title">
            <span class="code-lang" style="color: {escape(badge_color)};">{escape(lang)}</span>
            <span>{escape(label)}</span>
          </div>
          <button class="copy-btn" onclick="copyCode(this)" type="button">copy</button>
        </div>
        <pre><code class="language-{escape(lang)}">{escape(code)}</code></pre>
      </div>
"""


def render_usage_section(usage_blocks: list[tuple[str, str, str]] | None) -> str:
    if not usage_blocks:
        return ""

    blocks_html = "".join(
        render_code_block(label, lang, code) for label, lang, code in usage_blocks
    )

    return f"""
    <section class="usage" aria-label="Usage examples">
      <div class="usage-title">usage</div>
{blocks_html}    </section>
"""


def render_author_meta(author_name: str, author_twitter_handle: str) -> str:
    twitter_handle = author_twitter_handle.lstrip("@")

    return f"""
  <meta name="author" content="{escape(author_name)}">
  <meta name="twitter:site" content="@{escape(twitter_handle)}">
  <meta name="twitter:creator" content="@{escape(twitter_handle)}">"""


def render_author_link_tags(author_github_url: str, author_email: str) -> str:
    return f"""
  <link rel="me" href="{escape(author_github_url)}">
  <link rel="author" href="mailto:{escape(author_email)}">"""


def render_author_jsonld(
    author_name: str,
    author_twitter_handle: str,
    author_email: str,
    author_github_url: str,
    site_name: str,
    base_url: str,
) -> str:
    twitter_handle = author_twitter_handle.lstrip("@")
    twitter_url = f"https://x.com/{twitter_handle}"
    payload = {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": site_name,
        "url": base_url,
        "creator": {
            "@type": "Person",
            "name": author_name,
            "email": f"mailto:{author_email}",
            "sameAs": [
                twitter_url,
                author_github_url,
            ],
        },
    }
    jsonld = json.dumps(payload, ensure_ascii=False, indent=2).replace("</", "<\\/")

    return f"""
  <script type="application/ld+json">
{jsonld}
  </script>"""


def render_footer_credit(
    author_name: str,
    author_twitter_handle: str,
    author_email: str,
    author_github_url: str,
) -> str:
    twitter_handle = author_twitter_handle.lstrip("@")
    twitter_url = f"https://x.com/{twitter_handle}"

    return (
        f'Made by <a href="{escape(author_github_url)}">{escape(author_name)}</a>'
        f' &middot; <a href="{escape(twitter_url)}">X</a>'
        f' &middot; <a href="mailto:{escape(author_email)}">{escape(author_email)}</a>'
    )


def render_page(
    *,
    title: str,
    description: str,
    path_text: str,
    canonical_url: str,
    favicon_url: str,
    site_name: str,
    base_url: str,
    rows_html: str,
    usage_blocks: list[tuple[str, str, str]] | None,
    generated_at: str,
    author_name: str,
    author_twitter_handle: str,
    author_email: str,
    author_github_url: str,
) -> str:
    usage_html = render_usage_section(usage_blocks)
    needs_groovy = bool(usage_blocks) and any(lang == "groovy" for _, lang, _ in usage_blocks)
    groovy_script = f'\n  <script src="{HLJS_JS_URL.rsplit("/", 1)[0]}/languages/groovy.min.js"></script>' if needs_groovy else ""

    author_meta = render_author_meta(author_name, author_twitter_handle)
    author_link_tags = render_author_link_tags(author_github_url, author_email)
    author_jsonld = render_author_jsonld(
        author_name, author_twitter_handle, author_email, author_github_url, site_name, base_url
    )
    footer_credit = render_footer_credit(
        author_name, author_twitter_handle, author_email, author_github_url
    )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{escape(title)}</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{escape(description)}">
  <meta name="robots" content="index, follow">
  <meta name="theme-color" content="#78e398">

  <link rel="canonical" href="{escape(canonical_url)}">
  <link rel="icon" href="{escape(favicon_url)}" type="image/x-icon">
  <link rel="shortcut icon" href="{escape(favicon_url)}" type="image/x-icon">

  <meta property="og:type" content="website">
  <meta property="og:title" content="{escape(title)}">
  <meta property="og:description" content="{escape(description)}">
  <meta property="og:url" content="{escape(canonical_url)}">
  <meta property="og:site_name" content="{escape(site_name)}">

  <meta name="twitter:card" content="summary">
  <meta name="twitter:title" content="{escape(title)}">
  <meta name="twitter:description" content="{escape(description)}">
{author_meta}
{author_link_tags}

  <link rel="stylesheet" href="{HLJS_CSS_URL}">
  <style>{PAGE_CSS}</style>
{author_jsonld}
</head>
<body>
  <main>
    <header>
      <h1>{escape(title)}</h1>
      <div class="subtitle">{escape(description)}</div>
      <div class="path">{escape(path_text)}</div>
    </header>
{usage_html}
    <section class="table-wrap" aria-label="Directory listing">
      <table>
        <tbody>
          {rows_html}
        </tbody>
      </table>
    </section>

    <footer>
      Generated at {escape(generated_at)}<br>
      {footer_credit}
    </footer>
  </main>

  <script src="{HLJS_JS_URL}"></script>{groovy_script}
  <script>{COPY_SCRIPT}</script>
</body>
</html>
"""
