from __future__ import annotations

import re
import urllib.error
import urllib.request
from datetime import datetime, timezone
from functools import lru_cache
from html import escape
from pathlib import Path

import html_renderer as render
import site_config as data


def display_path(root: Path, directory: Path) -> str:
    if directory == root:
        return "/"
    return "/" + directory.relative_to(root).as_posix().strip("/") + "/"


def canonical_url(root: Path, directory: Path) -> str:
    path = display_path(root, directory)
    if path == "/":
        return data.BASE_URL + "/"
    return data.BASE_URL + path


def maven_url(root: Path) -> str | None:
    if (root / "maven").exists():
        return data.BASE_URL + "/maven/"
    return None


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


def is_app_page_dir(root: Path, directory: Path) -> bool:
    try:
        parts = directory.relative_to(root).parts
    except ValueError:
        return False
    return len(parts) >= 2 and parts[0] == "apps"


def has_existing_index(directory: Path) -> bool:
    return (directory / "index.html").exists()


def is_maven_tree(root: Path, directory: Path) -> bool:
    try:
        return directory.relative_to(root).parts[0] == "maven"
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
    if suffixes.endswith((".tar.xz", ".tar.gz", ".tar.zst")):
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


def row_class(kind: str) -> str:
    return "row-" + re.sub(r"[^a-z0-9]+", "-", kind.lower()).strip("-")


def visible_children(root: Path, directory: Path) -> list[Path]:
    children: list[Path] = []

    for child in sorted(directory.iterdir(), key=lambda p: (p.is_file(), p.name.lower())):
        if is_hidden_or_ignored(child):
            continue

        if child.is_dir():
            if directory == root and not is_visible_root_dir(child):
                continue
            children.append(child)
            continue

        children.append(child)

    return children


@lru_cache(maxsize=None)
def fetch_remote_text(url: str) -> str | None:
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


def page_description(root: Path, directory: Path) -> str:
    path = display_path(root, directory)

    if path == "/":
        return (
            "Public package repository for TamKungZ_ projects, including APT, RPM, "
            "Alpine APK, Void XBPS, Arch pacman repositories, release assets, "
            "signatures, and metadata."
        )

    if path.startswith("/apt/") or path == "/apt/":
        return "APT repository shared by TamKungZ_ Linux packages."
    if path.startswith("/rpm/") or path == "/rpm/":
        return "RPM repository shared by TamKungZ_ Linux packages."
    if path.startswith("/apk/") or path == "/apk/":
        return "Alpine APK repository shared by TamKungZ_ Linux packages."
    if path.startswith("/xbps/") or path == "/xbps/":
        return "Void Linux XBPS repository shared by TamKungZ_ Linux packages."
    if path.startswith("/arch/") or path == "/arch/":
        return "Arch Linux pacman repository shared by TamKungZ_ Linux packages."

    if path == "/apps/":
        return "Human-readable app pages. Package downloads are served from /apt, /rpm, /apk, /xbps, and /arch."

    if path.startswith("/apps/"):
        app_name = directory.name
        summary = read_remote_readme_summary(app_name) or read_local_readme_summary(directory)
        if summary:
            return summary
        return f"Human-readable package page for {app_name}."

    return f"Browse public package files in {path}."


def page_usage(root: Path, directory: Path) -> list[tuple[str, str, str]] | None:
    path = display_path(root, directory)

    if path == "/":
        return data.root_usage_blocks(data.BASE_URL, maven_url(root))
    if path == "/apps/tarminal/":
        return data.tarminal_usage_blocks(data.BASE_URL)

    return None


def make_index(root: Path, directory: Path, generated_pages: list[Path]) -> None:
    path_text = display_path(root, directory)
    title = data.SITE_NAME if path_text == "/" else f"{data.SITE_NAME} - {path_text}"
    description = page_description(root, directory)
    now = datetime.now(timezone.utc).isoformat()
    usage_blocks = page_usage(root, directory)

    rows: list[str] = []

    if directory != root:
        rows.append(
            """\
            <tr class="row-directory">
              <td class="type">dir</td>
              <td class="name"><a href="../">../</a></td>
              <td class="size"></td>
            </tr>"""
        )

    for child in visible_children(root, directory):
        name = child.name + ("/" if child.is_dir() else "")
        href = child.name + ("/" if child.is_dir() else "")
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

    html = render.render_page(
        title=title,
        description=description,
        path_text=path_text,
        canonical_url=canonical_url(root, directory),
        favicon_svg_url=data.FAVICON_SVG_URL,
        favicon_ico_url=data.FAVICON_ICO_URL,
        theme_color=data.THEME_COLOR,
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
    generated_pages.append(directory)


def generate_package_pages(root: Path) -> list[Path]:
    generated_pages: list[Path] = []
    make_index(root, root, generated_pages)

    for directory in sorted(root.rglob("*")):
        if not directory.is_dir():
            continue

        if is_maven_tree(root, directory):
            continue

        relative_parts = directory.relative_to(root).parts
        if any(part in data.IGNORE_DIRS for part in relative_parts):
            continue
        if any(part.startswith(".") and part not in {".well-known"} for part in relative_parts):
            continue

        if has_existing_index(directory):
            try:
                parts = directory.relative_to(root).parts
                if len(parts) >= 2 and parts[0] == "apps":
                    generated_pages.append(directory)
                    continue
            except (ValueError, IndexError):
                pass

        if is_app_page_dir(root, directory) and has_existing_index(directory):
            generated_pages.append(directory)
            continue

        make_index(root, directory, generated_pages)

    return generated_pages
