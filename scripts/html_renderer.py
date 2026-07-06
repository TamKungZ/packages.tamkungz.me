"""HTML rendering for the package index site.

This module owns presentation only: given plain data (title, description,
rows, usage blocks, ...) it returns a full HTML document as a string. It
does not touch the filesystem and does not know about directory scanning.
"""

from __future__ import annotations

import json
from html import escape

# Small accent per language so each block's badge reads at a glance.
LANG_BADGE_COLORS = {
    "bash": "#03983d",
    "groovy": "#7a5b12",
    "ini": "#245b91",
}
DEFAULT_BADGE_COLOR = "#5f6d5f"

PAGE_CSS = """
:root {
  color-scheme: light;
  --bg: #ffffff;
  --panel: #ffffff;
  --panel-2: #f3fff7;
  --text: #172017;
  --muted: #5e6d61;
  --line: #b9dfc8;
  --line-soft: #e0f2e6;
  --line-strong: #03983d;
  --accent: #03983d;
  --accent-dark: #026b2c;
  --accent-soft: #e8fbef;
  --code-bg: #ffffff;
}

* { box-sizing: border-box; }

body {
  margin: 0;
  background: var(--bg);
  color: var(--text);
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace;
  font-size: 14px;
  line-height: 1.45;
}

body::before {
  content: "";
  display: block;
  height: 6px;
  background: var(--accent);
}

main {
  width: min(1180px, calc(100% - 28px));
  margin: 18px auto 28px;
}

header {
  margin-bottom: 14px;
  padding-bottom: 10px;
  border-bottom: 2px solid var(--line-strong);
}

h1 {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
  letter-spacing: 0;
  line-height: 1.15;
}

.subtitle {
  margin-top: 6px;
  color: var(--muted);
  max-width: 1000px;
}

.path {
  display: inline-flex;
  align-items: center;
  margin-top: 8px;
  padding: 2px 7px;
  border: 1px solid var(--line);
  border-radius: 3px;
  background: var(--panel-2);
  color: var(--accent-dark);
  font-size: 12px;
}

.table-wrap {
  overflow: auto;
  border: 1px solid var(--line);
  border-radius: 4px;
  background: var(--panel);
}

table {
  width: 100%;
  border-collapse: collapse;
}

td {
  padding: 6px 10px;
  border-bottom: 1px solid var(--line-soft);
  vertical-align: middle;
}

tr:last-child td { border-bottom: 0; }
tr:hover { background: #f0f6ec; }

.type {
  width: 120px;
  color: var(--muted);
  text-transform: uppercase;
  font-size: 11px;
  letter-spacing: 0.06em;
}

.name { word-break: break-all; }

.name a {
  color: var(--text);
}

.row-directory .name a {
  color: var(--accent-dark);
  font-weight: 700;
}

.size {
  width: 150px;
  color: var(--muted);
  text-align: right;
  white-space: nowrap;
}

a {
  color: var(--accent);
  text-decoration: none;
}

a:hover {
  color: var(--accent-dark);
  text-decoration: underline;
}

.install {
  margin: 14px 0 14px;
  border: 1px solid var(--line);
  border-radius: 4px;
  background: var(--panel);
}

.install-title {
  padding: 7px 10px;
  border-bottom: 1px solid var(--line-strong);
  background: var(--accent);
  color: #ffffff;
  font-weight: 700;
}

.install-body {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(420px, 100%), 1fr));
  gap: 10px;
  padding: 10px;
}

.code-block {
  border: 1px solid var(--line);
  border-radius: 3px;
  background: var(--panel);
  overflow: hidden;
}

.code-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 5px 8px;
  border-bottom: 1px solid var(--line);
  background: var(--panel-2);
}

.code-title {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
  color: var(--muted);
  font-size: 12px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.code-lang {
  flex: none;
  padding: 1px 6px;
  border: 1px solid currentColor;
  border-radius: 3px;
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.copy-btn {
  flex: none;
  font: inherit;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--muted);
  background: transparent;
  border: 1px solid var(--line);
  border-radius: 3px;
  padding: 2px 8px;
  cursor: pointer;
  transition: color 0.15s ease, border-color 0.15s ease, background 0.15s ease;
}

.copy-btn:hover {
  color: var(--accent-dark);
  border-color: var(--accent-dark);
  background: var(--accent-soft);
}

.copy-btn.copied {
  color: var(--accent-dark);
  border-color: var(--accent-dark);
  background: var(--accent-soft);
}

.code-block pre {
  margin: 0;
  padding: 8px 10px;
  overflow: auto;
  max-height: 210px;
  background: var(--code-bg);
}

.code-block code {
  color: var(--text);
  font-family: inherit;
  font-size: 13px;
  white-space: pre;
}

footer {
  margin-top: 14px;
  padding-top: 10px;
  border-top: 1px solid var(--line);
  color: var(--muted);
  font-size: 12px;
}

@media (max-width: 640px) {
  main {
    width: min(100% - 16px, 1180px);
    margin-top: 12px;
  }

  h1 { font-size: 21px; }
  td { padding: 6px 8px; }
  .type { width: 82px; }
  .size { display: none; }
  .code-title span:last-child { display: none; }
  .install-body { display: block; }
  .code-block { margin-bottom: 10px; }
  .code-block:last-child { margin-bottom: 0; }
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
    <section class="install" aria-label="Install examples">
      <div class="install-title">Install</div>
      <div class="install-body">
{blocks_html}      </div>
    </section>
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
    favicon_svg_url: str,
    favicon_ico_url: str,
    theme_color: str,
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
  <meta name="theme-color" content="{escape(theme_color)}">

  <link rel="canonical" href="{escape(canonical_url)}">
  <link rel="icon" href="{escape(favicon_svg_url)}" type="image/svg+xml">
  <link rel="icon" href="{escape(favicon_ico_url)}" sizes="any">
  <link rel="shortcut icon" href="{escape(favicon_ico_url)}" type="image/x-icon">

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

  <script>{COPY_SCRIPT}</script>
</body>
</html>
"""
