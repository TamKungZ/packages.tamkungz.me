from pathlib import Path
from html import escape
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent.parent

SITE_NAME = "TamKungZ_ Maven Repository (Permanent)"
BASE_URL = "https://maven.tamkungz.me"
FAVICON_URL = "https://pub-df28fb9f69aa4326a1c6e10fb1f2abdc.r2.dev/assets-image/maven/tamkungz-repo-favicon-v2-nobg.ico"

# Maven group roots that should be visible from /
MAVEN_ROOTS = [
    ROOT / "me",
]

IGNORE_DIRS = {
    ".git",
    ".github",
    "scripts",
    "examples",
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

ALLOWED_FILE_SUFFIXES = {
    ".jar",
    ".pom",
    ".module",
    ".xml",
    ".sha1",
    ".md5",
    ".asc",
}

GENERATED_PAGES = []


def display_path(directory: Path) -> str:
    if directory == ROOT:
        return "/"
    return "/" + directory.relative_to(ROOT).as_posix().strip("/") + "/"


def canonical_url(directory: Path) -> str:
    path = display_path(directory)
    if path == "/":
        return BASE_URL + "/"
    return BASE_URL + path


def page_description(directory: Path) -> str:
    path = display_path(directory)

    if path == "/":
        return (
            "Public Maven repository for TamKungZ projects. "
            "Use this repository with Gradle, Maven, Forge, Fabric, NeoForge, "
            "and other JVM build tools."
        )

    return f"Browse Maven artifacts in {path} from the TamKungZ Maven Repository."


def is_inside_maven_root(path: Path) -> bool:
    try:
        path.relative_to(ROOT)
    except ValueError:
        return False

    for maven_root in MAVEN_ROOTS:
        try:
            path.relative_to(maven_root)
            return True
        except ValueError:
            continue

    return False


def is_visible_root_dir(path: Path) -> bool:
    return any(path == maven_root for maven_root in MAVEN_ROOTS)


def is_maven_file(path: Path) -> bool:
    if path.name in IGNORE_FILES:
        return False

    if path.name == "maven-metadata.xml":
        return True

    if path.suffix in ALLOWED_FILE_SUFFIXES:
        return True

    return False


def file_size(path: Path) -> str:
    size = path.stat().st_size

    if size >= 1024 * 1024:
        return f"{size / (1024 * 1024):.2f} MB"

    if size >= 1024:
        return f"{size / 1024:.2f} KB"

    return f"{size:,} bytes"


def file_kind(path: Path) -> str:
    if path.is_dir():
        return "directory"

    suffix = path.suffix.lower()

    if suffix == ".jar":
        return "jar"
    if suffix == ".pom":
        return "pom"
    if suffix == ".module":
        return "module"
    if suffix in {".sha1", ".md5"}:
        return "checksum"
    if suffix == ".asc":
        return "signature"
    if path.name == "maven-metadata.xml":
        return "metadata"

    return "file"


def visible_children(directory: Path):
    children = []

    for child in sorted(directory.iterdir(), key=lambda p: (p.is_file(), p.name.lower())):
        if child.name in IGNORE_FILES:
            continue

        if child.is_dir():
            if child.name in IGNORE_DIRS:
                continue

            if directory == ROOT and not is_visible_root_dir(child):
                continue

            if directory != ROOT and not is_inside_maven_root(child):
                continue

            children.append(child)
            continue

        if directory == ROOT:
            continue

        if not is_maven_file(child):
            continue

        children.append(child)

    return children


def make_index(directory: Path):
    path_text = display_path(directory)
    title = SITE_NAME if path_text == "/" else f"{SITE_NAME} - {path_text}"
    description = page_description(directory)
    now = datetime.now(timezone.utc).isoformat()

    rows = []

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

    gradle_block = """repositories {
    maven {
        name = "TamKungZ Maven"
        url = uri("https://maven.tamkungz.me/")
    }
}"""

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

    * {{
      box-sizing: border-box;
    }}

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

    header {{
      margin-bottom: 28px;
    }}

    h1 {{
      margin: 0;
      font-size: clamp(28px, 4vw, 42px);
      letter-spacing: -0.04em;
      line-height: 1.1;
    }}

    .subtitle {{
      margin-top: 10px;
      color: var(--muted);
      max-width: 760px;
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

    tr:last-child td {{
      border-bottom: 0;
    }}

    tr:hover {{
      background: var(--accent-soft);
    }}

    .type {{
      width: 120px;
      color: var(--muted);
      text-transform: uppercase;
      font-size: 12px;
      letter-spacing: 0.08em;
    }}

    .name {{
      word-break: break-all;
    }}

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

    a:hover {{
      text-decoration: underline;
    }}

    footer {{
      margin-top: 28px;
      color: var(--muted);
      font-size: 13px;
    }}

    @media (max-width: 640px) {{
      main {{
        margin: 28px auto;
      }}

      td {{
        padding: 10px;
      }}

      .type {{
        width: 82px;
      }}

      .size {{
        display: none;
      }}
    }}
  </style>
</head>
<body>
  <main>
    <header>
      <h1>TamKungZ_ Maven Repository (Permanent)</h1>
      <div class="subtitle">{escape(description)}</div>
      <div class="path">{escape(path_text)}</div>
    </header>

    <section class="usage" aria-label="Gradle repository example">
      <pre>{escape(gradle_block)}</pre>
    </section>

    <section class="table-wrap" aria-label="Maven directory listing">
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


def write_robots():
    content = f"""User-agent: *
Allow: /

Sitemap: {BASE_URL}/sitemap.xml
"""
    (ROOT / "robots.txt").write_text(content, encoding="utf-8")


def write_sitemap():
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


def main():
    make_index(ROOT)

    for maven_root in MAVEN_ROOTS:
        if not maven_root.exists():
            continue

        make_index(maven_root)

        for directory in maven_root.rglob("*"):
            if directory.is_dir():
                make_index(directory)

    write_robots()
    write_sitemap()


if __name__ == "__main__":
    main()