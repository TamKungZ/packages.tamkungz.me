from __future__ import annotations

import os
from datetime import datetime, timezone
from html import escape
from pathlib import Path

import maven_pages
import package_pages
import html_renderer as render
import site_config as data


def find_repo_root() -> Path:
    """Return the package-site root in release.yml and local runs.

    The publish job runs this after cd-ing into the cloned packages-site repo.
    PACKAGE_INDEX_ROOT exists for local tests that need a temporary root.
    """
    explicit_root = os.environ.get("PACKAGE_INDEX_ROOT")
    if explicit_root:
        return Path(explicit_root).resolve()

    return Path(__file__).resolve().parent.parent


def display_path(root: Path, directory: Path) -> str:
    if directory == root:
        return "/"
    return "/" + directory.relative_to(root).as_posix().strip("/") + "/"


def canonical_url(root: Path, directory: Path) -> str:
    path = display_path(root, directory)
    if path == "/":
        return data.BASE_URL + "/"
    return data.BASE_URL + path


PACKAGE_ROOT_ORDER = {
    "apt": 0,
    "arch": 1,
    "maven": 2,
    "rpm": 3,
    "apk": 4,
    "xbps": 5,
}


def path_parts(root: Path, directory: Path) -> tuple[str, ...]:
    if directory == root:
        return ()
    return directory.relative_to(root).parts


def sitemap_priority(root: Path, directory: Path) -> float:
    parts = path_parts(root, directory)

    if not parts:
        return 1.0
    if len(parts) == 2 and parts[0] == "apps":
        return 0.95
    if parts == ("apps",):
        return 0.9
    if len(parts) == 1 and parts[0] in PACKAGE_ROOT_ORDER:
        return 0.75
    if parts and parts[0] in PACKAGE_ROOT_ORDER:
        return 0.45

    return 0.3


def sitemap_sort_key(root: Path, directory: Path) -> tuple[int, int, str]:
    parts = path_parts(root, directory)
    path = display_path(root, directory)

    if not parts:
        return (0, 0, path)
    if len(parts) == 2 and parts[0] == "apps":
        return (1, 0, path)
    if parts == ("apps",):
        return (2, 0, path)
    if parts and parts[0] in PACKAGE_ROOT_ORDER:
        return (3, PACKAGE_ROOT_ORDER[parts[0]], path)

    return (4, 0, path)


def write_robots(root: Path) -> None:
    content = f"""User-agent: *
Allow: /

Sitemap: {data.BASE_URL}/sitemap.xml
"""
    (root / "robots.txt").write_text(content, encoding="utf-8")


def write_sitemap(root: Path, generated_pages: list[Path]) -> None:
    now = datetime.now(timezone.utc).date().isoformat()
    unique_pages = list(dict.fromkeys(generated_pages))

    urls = []
    for directory in sorted(unique_pages, key=lambda p: sitemap_sort_key(root, p)):
        urls.append(
            f"""  <url>
    <loc>{escape(canonical_url(root, directory))}</loc>
    <lastmod>{now}</lastmod>
    <priority>{sitemap_priority(root, directory):.2f}</priority>
  </url>"""
        )

    content = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{chr(10).join(urls)}
</urlset>
"""
    (root / "sitemap.xml").write_text(content, encoding="utf-8")


def ensure_legal_directories(root: Path) -> None:
    for page in data.LEGAL_PAGES:
        (root / str(page["slug"])).mkdir(exist_ok=True)


def write_legal_pages(root: Path) -> list[Path]:
    now = datetime.now(timezone.utc).isoformat()
    written_pages: list[Path] = []

    for page in data.LEGAL_PAGES:
        slug = str(page["slug"])
        directory = root / slug
        directory.mkdir(exist_ok=True)
        path_text = display_path(root, directory)
        html = render.render_document_page(
            title=f"{data.SITE_NAME} - {page['title']}",
            description=str(page["description"]),
            path_text=path_text,
            canonical_url=canonical_url(root, directory),
            favicon_svg_url=data.FAVICON_SVG_URL,
            favicon_ico_url=data.FAVICON_ICO_URL,
            theme_color=data.THEME_COLOR,
            site_name=data.SITE_NAME,
            base_url=data.BASE_URL,
            sections=page["sections"],  # type: ignore[arg-type]
            generated_at=now,
            author_name=data.AUTHOR_NAME,
            author_twitter_handle=data.AUTHOR_TWITTER_HANDLE,
            author_email=data.AUTHOR_EMAIL,
            author_github_url=data.AUTHOR_GITHUB_URL,
        )
        (directory / "index.html").write_text(html, encoding="utf-8")
        written_pages.append(directory)

    return written_pages


def build_site(root: Path | None = None) -> list[Path]:
    root = root or find_repo_root()
    (root / ".nojekyll").touch()
    ensure_legal_directories(root)

    generated_pages = package_pages.generate_package_pages(root)
    generated_pages.extend(maven_pages.generate_maven_pages(root))
    generated_pages.extend(write_legal_pages(root))

    write_robots(root)
    write_sitemap(root, generated_pages)
    return generated_pages


def main() -> None:
    build_site()


if __name__ == "__main__":
    main()
