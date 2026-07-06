from __future__ import annotations

import importlib.util
import os
import re
import urllib.error
import urllib.request
from datetime import datetime, timezone
from functools import lru_cache
from html import escape
from pathlib import Path

import pkg_data as data
import pkg_render as render



def find_repo_root() -> Path:
    """Return the package-site root in release.yml and local runs.

    release.yml runs this as scripts/generate-package-indexes.py after cd-ing
    into the cloned packages.tamkungz.me repo, while local testing often runs
    it directly from the repo root.  Do not use GITHUB_WORKSPACE here: in the
    publish job that variable points to the source repo, not packages-site.
    """
    explicit_root = os.environ.get("PACKAGE_INDEX_ROOT")
    if explicit_root:
        return Path(explicit_root).resolve()

    script_dir = Path(__file__).resolve().parent
    if script_dir.name == "scripts":
        return script_dir.parent
    return script_dir


ROOT = find_repo_root()

GENERATED_PAGES: list[Path] = []


# --- Path helpers --------------------------------------------------------


def display_path(directory: Path) -> str:
    if directory == ROOT:
        return "/"
    return "/" + directory.relative_to(ROOT).as_posix().strip("/") + "/"


def canonical_url(directory: Path) -> str:
    path = display_path(directory)
    if path == "/":
        return data.BASE_URL + "/"
    return data.BASE_URL + path


def maven_url() -> str | None:
    if (ROOT / "maven").exists():
        return data.BASE_URL + "/maven/"
    if (ROOT / "me").exists():
        return data.BASE_URL + "/"
    return None


# --- Filesystem scanning --------------------------------------------------


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
    if name in data.IGNORE_FILES or name in data.IGNORE_DIRS:
        return True
    if name.startswith(".") and name not in {".well-known"}:
        return True
    return False


def is_visible_root_dir(path: Path) -> bool:
    return path.name in data.PROJECT_ROOTS


def is_app_page_dir(directory: Path) -> bool:
    """True for any directory under /apps/ that should be hand-authored.
    
    App pages are meant to be hand-authored (see PROJECT_ROOTS docs in
    pkg_data.py), so the generator should never overwrite an index.html
    someone already wrote there."""
    try:
        parts = directory.relative_to(ROOT).parts
    except ValueError:
        return False
    return len(parts) >= 2 and parts[0] == "apps"


def has_existing_index(directory: Path) -> bool:
    return (directory / "index.html").exists()


def is_maven_tree(directory: Path) -> bool:
    try:
        return directory.relative_to(ROOT).parts[0] == "maven"
    except (ValueError, IndexError):
        return False


def file_kind(path: Path) -> str:
    if path.is_dir():
        return "directory"

    name = path.name.lower()
    suffixes = "".join(path.suffixes).lower()
    suffix = path.suffix.lower()

    if name == "gpg.key":
        return "gpg key"
    if name.endswith((".rsa.pub", ".pem.pub")) or suffix == ".pub":
        return "public key"
    if name == "sha256sums":
        return "checksum"

    if name in {"inrelease", "release", "release.gpg"}:
        return "apt metadata"
    if name == "packages" or name == "packages.gz":
        return "apt index"
    if name == "apkindex.tar.gz":
        return "apk index"
    if name.endswith((".db", ".db.tar.gz", ".files", ".files.tar.gz")):
        return "pacman metadata"
    if name == "repomd.xml" or name == "repomd.xml.asc":
        return "rpm metadata"

    if suffix == ".rpm":
        return "rpm"
    if suffix == ".deb":
        return "deb"
    if suffix == ".apk":
        return "apk"
    if suffix == ".xbps":
        return "xbps"
    if suffixes.endswith(".pkg.tar.zst"):
        return "pacman package"
    if suffix == ".snap":
        return "snap"
    if suffix == ".flatpak":
        return "flatpak"
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
    if suffix in {".asc", ".sig"}:
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


# --- README summaries (local + remote) -----------------------------------


@lru_cache(maxsize=None)
def fetch_remote_text(url: str) -> str | None:
    """Best-effort fetch. Returns None on any failure so a flaky network
    never breaks the whole build - the caller falls back to a generic
    description instead."""
    request = urllib.request.Request(
        url, headers={"User-Agent": "tamkungz-packages-index-generator"}
    )
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            return response.read().decode("utf-8", errors="replace")
    except (urllib.error.URLError, TimeoutError, ValueError):
        return None


def strip_inline_markdown(text: str) -> str:
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"\*\*([^*]*)\*\*", r"\1", text)
    text = re.sub(r"__([^_]*)__", r"\1", text)
    text = re.sub(r"\*([^*]*)\*", r"\1", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    return text


def summarize_readme_text(text: str) -> str | None:
    text = text.strip()
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

    return strip_inline_markdown(" ".join(lines))


def read_local_readme_summary(directory: Path) -> str | None:
    readme = directory / "README.md"
    if not readme.exists():
        return None

    text = readme.read_text(encoding="utf-8", errors="replace")
    return summarize_readme_text(text)


def read_remote_readme_summary(app_name: str) -> str | None:
    url = data.APP_README_SOURCES.get(app_name)
    if not url:
        return None

    text = fetch_remote_text(url)
    if not text:
        return None

    return summarize_readme_text(text)


# --- Page content ----------------------------------------------------


def page_description(directory: Path) -> str:
    path = display_path(directory)

    if path == "/":
        return (
            "Public package repository for TamKungZ_ projects, including APT, RPM, "
            "Alpine APK, Void XBPS, Arch pacman repositories, release assets, "
            "signatures, and metadata."
        )

    if path == "/apt/" or path.startswith("/apt/"):
        return "APT repository shared by TamKungZ_ Linux packages."

    if path == "/rpm/" or path.startswith("/rpm/"):
        return "RPM repository shared by TamKungZ_ Linux packages."

    if path == "/apk/" or path.startswith("/apk/"):
        return "Alpine APK repository shared by TamKungZ_ Linux packages."

    if path == "/xbps/" or path.startswith("/xbps/"):
        return "Void Linux XBPS repository shared by TamKungZ_ Linux packages."

    if path == "/arch/" or path.startswith("/arch/"):
        return "Arch Linux pacman repository shared by TamKungZ_ Linux packages."

    if path == "/apps/":
        return "Human-readable app pages. Package downloads are served from /apt, /rpm, /apk, /xbps, and /arch."

    if path.startswith("/apps/"):
        app_name = directory.name
        summary = read_remote_readme_summary(app_name) or read_local_readme_summary(directory)
        if summary:
            return summary
        return f"Human-readable package page for {app_name}."

    if path.startswith("/maven/"):
        return "Maven artifacts for TamKungZ_ JVM projects."

    return f"Browse public package files in {path}."


def page_usage(directory: Path) -> list[tuple[str, str, str]] | None:
    path = display_path(directory)

    if path == "/":
        return data.root_usage_blocks(data.BASE_URL, maven_url())
    if path == "/apps/tarminal/":
        return data.tarminal_usage_blocks(data.BASE_URL)
    if path.startswith("/maven/"):
        repo_url = maven_url() or data.BASE_URL + "/"
        return data.maven_usage_blocks(repo_url)

    return None


# --- Page generation -------------------------------------------------


def make_index(directory: Path) -> None:
    path_text = display_path(directory)
    title = data.SITE_NAME if path_text == "/" else f"{data.SITE_NAME} - {path_text}"
    description = page_description(directory)
    now = datetime.now(timezone.utc).isoformat()
    usage_blocks = page_usage(directory)

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

    html = render.render_page(
        title=title,
        description=description,
        path_text=path_text,
        canonical_url=canonical_url(directory),
        favicon_url=data.FAVICON_URL,
        site_name=data.SITE_NAME,
        base_url=data.BASE_URL,
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


def write_robots() -> None:
    content = f"""User-agent: *
Allow: /

Sitemap: {data.BASE_URL}/sitemap.xml
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


def generate_maven_indexes() -> list[Path]:
    maven_script = Path(__file__).resolve().parent / "generate-maven-indexes.py"
    if not maven_script.exists():
        return []

    spec = importlib.util.spec_from_file_location("generate_maven_indexes", maven_script)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {maven_script}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module.generate_indexes()


def main() -> None:
    (ROOT / ".nojekyll").touch()

    make_index(ROOT)

    for directory in sorted(ROOT.rglob("*")):
        if not directory.is_dir():
            continue

        if is_maven_tree(directory):
            continue

        relative_parts = directory.relative_to(ROOT).parts
        if any(part in data.IGNORE_DIRS for part in relative_parts):
            continue
        if any(part.startswith(".") and part not in {".well-known"} for part in relative_parts):
            continue

        # Skip any directory under /apps/ that already has index.html
        if has_existing_index(directory):
            try:
                if directory.relative_to(ROOT).parts[0] == "apps":
                    GENERATED_PAGES.append(directory)
                    continue
            except (ValueError, IndexError):
                pass

        if is_app_page_dir(directory) and has_existing_index(directory):
            # Hand-authored app page - keep it as-is, but still list it in
            # the sitemap so it's discoverable.
            GENERATED_PAGES.append(directory)
            continue

        make_index(directory)

    GENERATED_PAGES.extend(generate_maven_indexes())

    write_robots()
    write_sitemap()


if __name__ == "__main__":
    main()
