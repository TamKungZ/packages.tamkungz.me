from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SITE_NAME = "TamKungZ_ Packages"
BASE_URL = "https://packages.tamkungz.me"
FAVICON_URL = "https://pub-df28fb9f69aa4326a1c6e10fb1f2abdc.r2.dev/assets-image/maven/tamkungz-repo-favicon-v2-nobg.ico"

# Root-level package repository layout:
# /apt              APT repository shared by all Debian packages
# /rpm/<basearch>   RPM repository shared by all RPM packages
# /maven            Maven repository, preferred new layout
# /me               Maven legacy group root, supported for compatibility
# /apps/<app>       human-readable product pages only
PROJECT_ROOTS = {
    "apt",
    "rpm",
    "maven",
    "me",  # legacy Maven group root
    "apps",
}

IGNORE_DIRS = {
    ".git",
    ".github",
    "scripts",
    "examples",
    "target",
    "node_modules",
    "__pycache__",
}

IGNORE_FILES = {
    "index.html",
    "CNAME",
    ".nojekyll",
    "README.md",
    "LICENSE",
    "404.html",
    "robots.txt",
    "sitemap.xml",
    "push.txt",
}

GENERATED_PAGES: list[Path] = []


def display_path(directory: Path) -> str:
    if directory == ROOT:
        return "/"
    return "/" + directory.relative_to(ROOT).as_posix().strip("/") + "/"


def canonical_url(directory: Path) -> str:
    path = display_path(directory)
    if path == "/":
        return BASE_URL + "/"
    return BASE_URL + path


def file_size(path: Path) -> str:
    size = path.stat().st_size

    if size >= 1024 * 1024 * 1024:
        return f"{size / (1024 * 1024 * 1024):.2f} GB"
    if size >= 1024 * 1024:
        return f"{size / (1024 * 1024):.2f} MB"
    if size >= 1024:
        return f"{size / 1024:.2f} KB"

    return f"{size:,} bytes"


def is_hidden_or_ignored(path: Path) -> bool:
    name = path.name
    if name in IGNORE_FILES or name in IGNORE_DIRS:
        return True
    if name.startswith(".") and name not in {".well-known"}:
        return True
    return False


def is_visible_root_dir(path: Path) -> bool:
    return path.name in PROJECT_ROOTS


def file_kind(path: Path) -> str:
    if path.is_dir():
        return "directory"

    name = path.name.lower()
    suffixes = "".join(path.suffixes).lower()
    suffix = path.suffix.lower()

    if name == "gpg.key":
        return "gpg key"
    if name in {"inrelease", "release", "release.gpg"}:
        return "apt metadata"
    if name == "packages" or name == "packages.gz":
        return "apt index"
    if name == "repomd.xml" or name == "repomd.xml.asc":
        return "rpm metadata"
    if suffix == ".rpm":
        return "rpm"
    if suffix == ".deb":
        return "deb"
    if suffixes.endswith(".tar.xz") or suffixes.endswith(".tar.gz") or suffixes.endswith(".tar.zst"):
        return "archive"
    if suffix == ".jar":
        return "jar"
    if suffix == ".pom":
        return "pom"
    if suffix == ".module":
        return "module"
    if suffix in {".sha1", ".sha256", ".sha512", ".md5"}:
        return "checksum"
    if suffix == ".asc":
        return "signature"
    if name == "maven-metadata.xml":
        return "metadata"
    if suffix in {".xml", ".gz", ".xz", ".zck", ".sqlite", ".solv"}:
        return "metadata"

    return "file"


def visible_children(directory: Path) -> list[Path]:
    children: list[Path] = []

    for child in sorted(directory.iterdir(), key=lambda p: (p.is_file(), p.name.lower())):
        if is_hidden_or_ignored(child):
            continue

        if child.is_dir():
            if directory == ROOT and not is_visible_root_dir(child):
                continue
            children.append(child)
            continue

        # Root-level files are allowed for shared files like /gpg.key.
        children.append(child)

    return children


def maven_url() -> str:
    if (ROOT / "maven").exists():
        return BASE_URL + "/maven/"
    return BASE_URL + "/"


def read_readme_summary(directory: Path) -> str | None:
    readme = directory / "README.md"
    if not readme.exists():
        return None

    text = readme.read_text(encoding="utf-8", errors="replace").strip()
    if not text:
        return None

    lines = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            if lines:
                break
            continue
        if line.startswith("#"):
            continue
        lines.append(line)

    if not lines:
        return None

    return " ".join(lines)


def page_description(directory: Path) -> str:
    path = display_path(directory)

    if path == "/":
        return (
            "Public package repository for TamKungZ_ projects, including Maven artifacts, "
            "APT packages, RPM packages, signatures, and release metadata."
        )

    if path == "/apt/" or path.startswith("/apt/"):
        return "APT repository shared by TamKungZ_ Linux packages."

    if path == "/rpm/" or path.startswith("/rpm/"):
        return "RPM repository shared by TamKungZ_ Linux packages."

    if path == "/apps/":
        return "Human-readable app pages. Package downloads are served from /apt and /rpm."

    if path.startswith("/apps/"):
        summary = read_readme_summary(directory)
        if summary:
            return summary
        app_name = directory.name
        return f"Human-readable package page for {app_name}."

    if path.startswith("/maven/") or path.startswith("/me/"):
        return "Maven artifacts for TamKungZ_ JVM projects."

    return f"Browse public package files in {path}."


def root_usage() -> str:
    return f"""# Debian / Ubuntu / Zorin
curl -fsSL {BASE_URL}/gpg.key | \\
  sudo gpg --dearmor -o /usr/share/keyrings/tamkungz-packages.gpg

echo "deb [arch=amd64 signed-by=/usr/share/keyrings/tamkungz-packages.gpg] {BASE_URL}/apt stable main" | \\
  sudo tee /etc/apt/sources.list.d/tamkungz-packages.list

sudo apt update
sudo apt install tarminal

# Fedora / RPM
sudo tee /etc/yum.repos.d/tamkungz-packages.repo >/dev/null <<'EOF'
[tamkungz-packages]
name=TamKungZ Packages
baseurl={BASE_URL}/rpm/$basearch/
enabled=1
gpgcheck=0
repo_gpgcheck=1
gpgkey={BASE_URL}/gpg.key
EOF

sudo dnf install tarminal

# Maven / Gradle
repositories {{
    maven {{
        name = "TamKungZ Packages"
        url = uri("{maven_url()}")
    }}
}}"""


def tarminal_usage() -> str:
    return f"""# Debian / Ubuntu / Zorin
curl -fsSL {BASE_URL}/gpg.key | \\
  sudo gpg --dearmor -o /usr/share/keyrings/tamkungz-packages.gpg

echo "deb [arch=amd64 signed-by=/usr/share/keyrings/tamkungz-packages.gpg] {BASE_URL}/apt stable main" | \\
  sudo tee /etc/apt/sources.list.d/tamkungz-packages.list

sudo apt update
sudo apt install tarminal

# Fedora / RPM
sudo tee /etc/yum.repos.d/tamkungz-packages.repo >/dev/null <<'EOF'
[tamkungz-packages]
name=TamKungZ Packages
baseurl={BASE_URL}/rpm/$basearch/
enabled=1
gpgcheck=0
repo_gpgcheck=1
gpgkey={BASE_URL}/gpg.key
EOF

sudo dnf install tarminal"""


def maven_usage() -> str:
    return f"""repositories {{
    maven {{
        name = "TamKungZ Packages"
        url = uri("{maven_url()}")
    }}
}}"""


def page_usage(directory: Path) -> str | None:
    path = display_path(directory)

    if path == "/":
        return root_usage()
    if path == "/apps/tarminal/":
        return tarminal_usage()
    if path.startswith("/maven/") or path.startswith("/me/"):
        return maven_usage()

    return None


def make_index(directory: Path) -> None:
    path_text = display_path(directory)
    title = SITE_NAME if path_text == "/" else f"{SITE_NAME} - {path_text}"
    description = page_description(directory)
    now = datetime.now(timezone.utc).isoformat()
    usage = page_usage(directory)

    rows: list[str] = []

    if directory != ROOT:
        rows.append(
            """
            <tr>
              <td class="type">dir</td>
              <td class="name"><a href="../">../</a></td>
              <td class="size"></td>
            </tr>
            """
        )

    for child in visible_children(directory):
        name = child.name + ("/" if child.is_dir() else "")
        href = child.name + ("/" if child.is_dir() else "")
        kind = file_kind(child)
        size = "" if child.is_dir() else file_size(child)

        rows.append(
            f"""
            <tr>
              <td class="type">{escape(kind)}</td>
              <td class="name"><a href="{escape(href)}">{escape(name)}</a></td>
              <td class="size">{escape(size)}</td>
            </tr>
            """
        )

    usage_block = ""
    if usage:
        usage_block = f"""
    <section class="usage" aria-label="Usage example">
      <pre>{escape(usage)}</pre>
    </section>
"""

    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{escape(title)}</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{escape(description)}">
  <meta name="robots" content="index, follow">
  <meta name="theme-color" content="#78e398">

  <link rel="canonical" href="{escape(canonical_url(directory))}">
  <link rel="icon" href="{escape(FAVICON_URL)}" type="image/x-icon">
  <link rel="shortcut icon" href="{escape(FAVICON_URL)}" type="image/x-icon">

  <meta property="og:type" content="website">
  <meta property="og:title" content="{escape(title)}">
  <meta property="og:description" content="{escape(description)}">
  <meta property="og:url" content="{escape(canonical_url(directory))}">
  <meta property="og:site_name" content="{escape(SITE_NAME)}">

  <meta name="twitter:card" content="summary">
  <meta name="twitter:title" content="{escape(title)}">
  <meta name="twitter:description" content="{escape(description)}">

  <style>
    :root {{
      color-scheme: dark;
      --bg: #0f0f0f;
      --panel: #151515;
      --panel-2: #1b1b1b;
      --text: #e8e8e8;
      --muted: #8f8f8f;
      --line: #2a2a2a;
      --accent: #78e398;
      --accent-soft: rgba(120, 227, 152, 0.12);
    }}

    * {{ box-sizing: border-box; }}

    body {{
      margin: 0;
      background:
        radial-gradient(circle at top left, rgba(169, 255, 175, 0.08), transparent 320px),
        var(--bg);
      color: var(--text);
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace;
      line-height: 1.6;
    }}

    main {{
      width: min(1040px, calc(100% - 32px));
      margin: 48px auto;
    }}

    header {{ margin-bottom: 28px; }}

    h1 {{
      margin: 0;
      font-size: clamp(28px, 4vw, 42px);
      letter-spacing: -0.04em;
      line-height: 1.1;
    }}

    .subtitle {{
      margin-top: 10px;
      color: var(--muted);
      max-width: 800px;
    }}

    .path {{
      display: inline-flex;
      align-items: center;
      margin-top: 20px;
      padding: 7px 11px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
      color: var(--accent);
      font-size: 14px;
    }}

    .usage {{
      margin: 22px 0 26px;
      padding: 16px;
      overflow-x: auto;
      border: 1px solid var(--line);
      border-radius: 12px;
      background: linear-gradient(180deg, var(--panel-2), var(--panel));
    }}

    pre {{
      margin: 0;
      color: #dcdcdc;
      white-space: pre;
    }}

    .table-wrap {{
      overflow: hidden;
      border: 1px solid var(--line);
      border-radius: 12px;
      background: rgba(15, 15, 15, 0.72);
    }}

    table {{
      width: 100%;
      border-collapse: collapse;
    }}

    td {{
      padding: 11px 14px;
      border-bottom: 1px solid var(--line);
      vertical-align: middle;
    }}

    tr:last-child td {{ border-bottom: 0; }}
    tr:hover {{ background: var(--accent-soft); }}

    .type {{
      width: 130px;
      color: var(--muted);
      text-transform: uppercase;
      font-size: 12px;
      letter-spacing: 0.08em;
    }}

    .name {{ word-break: break-all; }}

    .size {{
      width: 160px;
      color: var(--muted);
      text-align: right;
      white-space: nowrap;
    }}

    a {{
      color: var(--accent);
      text-decoration: none;
    }}

    a:hover {{ text-decoration: underline; }}

    footer {{
      margin-top: 28px;
      color: var(--muted);
      font-size: 13px;
    }}

    @media (max-width: 640px) {{
      main {{ margin: 28px auto; }}
      td {{ padding: 10px; }}
      .type {{ width: 90px; }}
      .size {{ display: none; }}
    }}
  </style>
</head>
<body>
  <main>
    <header>
      <h1>{escape(title)}</h1>
      <div class="subtitle">{escape(description)}</div>
      <div class="path">{escape(path_text)}</div>
    </header>
{usage_block}
    <section class="table-wrap" aria-label="Directory listing">
      <table>
        <tbody>
          {''.join(rows)}
        </tbody>
      </table>
    </section>

    <footer>
      Generated at {escape(now)}
    </footer>
  </main>
</body>
</html>
"""

    (directory / "index.html").write_text(html, encoding="utf-8")
    GENERATED_PAGES.append(directory)


def write_robots() -> None:
    content = f"""User-agent: *
Allow: /

Sitemap: {BASE_URL}/sitemap.xml
"""
    (ROOT / "robots.txt").write_text(content, encoding="utf-8")


def write_sitemap() -> None:
    now = datetime.now(timezone.utc).date().isoformat()

    urls = []
    for directory in sorted(GENERATED_PAGES, key=lambda p: display_path(p)):
        urls.append(
            f"""  <url>
    <loc>{escape(canonical_url(directory))}</loc>
    <lastmod>{now}</lastmod>
  </url>"""
        )

    content = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{chr(10).join(urls)}
</urlset>
"""
    (ROOT / "sitemap.xml").write_text(content, encoding="utf-8")


def main() -> None:
    (ROOT / ".nojekyll").touch()

    make_index(ROOT)

    for directory in sorted(ROOT.rglob("*")):
        if not directory.is_dir():
            continue

        relative_parts = directory.relative_to(ROOT).parts
        if any(part in IGNORE_DIRS for part in relative_parts):
            continue
        if any(part.startswith(".") and part not in {".well-known"} for part in relative_parts):
            continue

        make_index(directory)

    write_robots()
    write_sitemap()


if __name__ == "__main__":
    main()
