from pathlib import Path
from html import escape
from datetime import datetime, timezone
import os
import re

import html_renderer as render
import site_config as data


def find_repo_root() -> Path:
    explicit_root = os.environ.get("PACKAGE_INDEX_ROOT")
    if explicit_root:
        return Path(explicit_root).resolve()

    return Path(__file__).resolve().parent.parent


ROOT = find_repo_root()
MAVEN_ROOT = ROOT / "maven"

SITE_NAME = "TamKungZ_ Stable Maven Repository"
BASE_URL = data.BASE_URL

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
    ".sha256",
    ".sha512",
    ".md5",
    ".asc",
}

GENERATED_PAGES: list[Path] = []


def configure_root(root: Path) -> None:
    global ROOT, MAVEN_ROOT
    ROOT = root
    MAVEN_ROOT = root / "maven"


def display_path(directory: Path) -> str:
    if directory == ROOT:
        return "/"
    if directory == MAVEN_ROOT:
        return "/maven/"

    try:
        relative = directory.relative_to(MAVEN_ROOT).as_posix().strip("/")
    except ValueError:
        relative = directory.relative_to(ROOT).as_posix().strip("/")

    return "/maven/" + relative + "/"


def canonical_url(directory: Path) -> str:
    path = display_path(directory)
    if path == "/":
        return BASE_URL + "/"
    return BASE_URL + path


def page_description(directory: Path) -> str:
    path = display_path(directory)

    if path == "/":
        return (
            "Public Maven repository for TamKungZ_ projects. "
            "Use this repository with Gradle, Maven, Forge, Fabric, NeoForge, "
            "and other JVM build tools."
        )

    return f"Browse Maven artifacts in {path} from the TamKungZ_ Stable Maven Repository."


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
    if suffix in {".sha1", ".sha256", ".sha512", ".md5"}:
        return "checksum"
    if suffix == ".asc":
        return "signature"
    if path.name == "maven-metadata.xml":
        return "metadata"

    return "file"


def row_class(kind: str) -> str:
    return "row-" + re.sub(r"[^a-z0-9]+", "-", kind.lower()).strip("-")


def visible_children(directory: Path):
    children = []

    for child in sorted(directory.iterdir(), key=lambda p: (p.is_file(), p.name.lower())):
        if child.name in IGNORE_FILES:
            continue

        if child.is_dir():
            if child.name in IGNORE_DIRS:
                continue
            children.append(child)
            continue

        if not is_maven_file(child):
            continue

        children.append(child)

    return children


def make_index(directory: Path):
    directory.mkdir(parents=True, exist_ok=True)
    path_text = display_path(directory)
    title = SITE_NAME if path_text == "/maven/" else f"{SITE_NAME} - {path_text}"
    description = page_description(directory)
    now = datetime.now(timezone.utc).isoformat()

    rows = []

    if directory != MAVEN_ROOT:
        rows.append(
            """\
            <tr class="row-directory">
              <td class="type">dir</td>
              <td class="name"><a href="../">../</a></td>
              <td class="size"></td>
            </tr>"""
        )

    for child in visible_children(directory):
        name = child.name + ("/" if child.is_dir() else "")
        href = f"{child.name}/" if child.is_dir() else child.name
        kind = file_kind(child)
        size = "" if child.is_dir() else file_size(child)

        rows.append(
            f"""\
            <tr class="{escape(row_class(kind))}">
              <td class="type">{escape(kind)}</td>
              <td class="name"><a href="{escape(href)}">{escape(name)}</a></td>
              <td class="size">{escape(size)}</td>
            </tr>"""
        )

    usage_blocks = [
        (
            "Maven / Gradle",
            "groovy",
            f"""repositories {{
    maven {{
        name = \"TamKungZ Maven\"
        url = uri(\"{data.BASE_URL}/maven/\")
    }}
}}""",
        )
    ]

    html = render.render_page(
        title=title,
        description=description,
        path_text=path_text,
        canonical_url=canonical_url(directory),
        favicon_svg_url=data.FAVICON_SVG_URL,
        favicon_ico_url=data.FAVICON_ICO_URL,
        theme_color=data.THEME_COLOR,
        site_name=SITE_NAME,
        base_url=BASE_URL,
        rows_html="".join(rows),
        usage_blocks=usage_blocks,
        generated_at=now,
        author_name=data.AUTHOR_NAME,
        author_twitter_handle=data.AUTHOR_TWITTER_HANDLE,
        author_email=data.AUTHOR_EMAIL,
        author_github_url=data.AUTHOR_GITHUB_URL,
    )

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


def generate_maven_pages(root: Path | None = None) -> list[Path]:
    if root is not None:
        configure_root(root)

    GENERATED_PAGES.clear()

    if not MAVEN_ROOT.exists():
        return []

    make_index(MAVEN_ROOT)

    for directory in sorted(MAVEN_ROOT.rglob("*")):
        if not directory.is_dir():
            continue
        make_index(directory)

    return GENERATED_PAGES.copy()


def generate_indexes(root: Path | None = None) -> list[Path]:
    return generate_maven_pages(root)


def main():
    generate_maven_pages()
    write_robots()
    write_sitemap()


if __name__ == "__main__":
    main()
