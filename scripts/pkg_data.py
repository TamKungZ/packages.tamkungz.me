"""Static configuration and content for the package index site.

This module intentionally contains no filesystem or network logic - it is
the "data" half of the generator. Anything here should be safe to read top
to bottom to understand what the site says, without needing to trace through
control flow.
"""

from __future__ import annotations

# --- Site identity -----------------------------------------------------

SITE_NAME = "TamKungZ_ Packages"
BASE_URL = "https://packages.tamkungz.me"
FAVICON_URL = "https://pub-df28fb9f69aa4326a1c6e10fb1f2abdc.r2.dev/assets-image/maven/tamkungz-repo-favicon-v2-nobg.ico"

# --- Author / SEO identity ---------------------------------------------

AUTHOR_NAME = "TamKungZ_"
AUTHOR_TWITTER_HANDLE = "@TamKungZ_"
AUTHOR_EMAIL = "dev@tamkungz.me"
AUTHOR_GITHUB_URL = "https://github.com/TamKungZ"

# --- Repository layout ---------------------------------------------------

# Root-level package repository layout.  release.yml currently publishes
# apt/rpm/apk/xbps/arch/apps; maven and me remain supported when the package
# site repo contains JVM artifacts.
# /apt              APT repository shared by all Debian packages
# /rpm/<basearch>   RPM repository shared by all RPM packages
# /apk/<arch>       Alpine APK repository
# /xbps/<arch>      Void Linux XBPS repository
# /arch/<arch>      Arch Linux pacman repository
# /maven            Maven repository, preferred new layout
# /me               Maven legacy group root, supported for compatibility
# /apps/<app>       human-readable product pages only
PROJECT_ROOTS = {
    "apt",
    "rpm",
    "apk",
    "xbps",
    "arch",
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

# --- Remote README sources -------------------------------------------

# Some /apps/<name>/ pages describe a project that lives in its own repo
# rather than in this one. For those, fetch the description straight from
# the upstream README instead of expecting a local README.md copy.
TARMINAL_README_URL = "https://raw.githubusercontent.com/TamKungZ/tarminal-tar-install/refs/heads/main/README.md"

APP_README_SOURCES = {
    "tarminal": TARMINAL_README_URL,
}

# --- Usage snippets ----------------------------------------------------
#
# Each "usage" block is (label, language, code). `language` should match a
# highlight.js language class (e.g. "bash", "groovy") so the rendered page
# can syntax-highlight it, and each block gets its own copy button.

UsageBlock = tuple[str, str, str]


def apt_usage_block(base_url: str) -> UsageBlock:
    return (
        "Debian / Ubuntu / Zorin",
        "bash",
        f"""curl -fsSL {base_url}/gpg.key | \\
  sudo gpg --dearmor -o /usr/share/keyrings/tamkungz-packages.gpg

echo "deb [arch=amd64 signed-by=/usr/share/keyrings/tamkungz-packages.gpg] {base_url}/apt stable main" | \\
  sudo tee /etc/apt/sources.list.d/tamkungz-packages.list

sudo apt update
sudo apt install tarminal""",
    )


def rpm_usage_block(base_url: str) -> UsageBlock:
    return (
        "Fedora / RPM",
        "bash",
        f"""sudo tee /etc/yum.repos.d/tamkungz-packages.repo >/dev/null <<'EOF'
[tamkungz-packages]
name=TamKungZ Packages
baseurl={base_url}/rpm/$basearch/
enabled=1
gpgcheck=0
repo_gpgcheck=1
gpgkey={base_url}/gpg.key
EOF

sudo dnf install tarminal""",
    )


def alpine_usage_block(base_url: str) -> UsageBlock:
    return (
        "Alpine APK",
        "bash",
        f"""sudo mkdir -p /etc/apk/keys
curl -fsSL {base_url}/apk/tamkungz.rsa.pub | \\
  sudo tee /etc/apk/keys/tamkungz.rsa.pub >/dev/null

echo "{base_url}/apk/$(apk --print-arch)" | \\
  sudo tee -a /etc/apk/repositories

sudo apk update
sudo apk add tarminal""",
    )


def void_usage_block(base_url: str) -> UsageBlock:
    return (
        "Void XBPS",
        "bash",
        f"""sudo mkdir -p /etc/xbps.d
sudo tee /etc/xbps.d/tamkungz.conf >/dev/null <<'EOF'
repository={base_url}/xbps/x86_64
EOF

sudo xbps-install -S
sudo xbps-install tarminal""",
    )


def arch_usage_block(base_url: str) -> UsageBlock:
    return (
        "Arch Linux",
        "bash",
        f"""curl -fsSL {base_url}/gpg.key | sudo pacman-key --add -
sudo pacman-key --lsign-key release@tamkungz.me || true

sudo tee -a /etc/pacman.conf >/dev/null <<'EOF'
[tamkungz]
Server = {base_url}/arch/$arch
SigLevel = DatabaseRequired PackageOptional
EOF

sudo pacman -Sy
sudo pacman -S tarminal""",
    )


def maven_usage_block(maven_repo_url: str) -> UsageBlock:
    return (
        "Maven / Gradle",
        "groovy",
        f"""repositories {{
    maven {{
        name = "TamKungZ Packages"
        url = uri("{maven_repo_url}")
    }}
}}""",
    )


def root_usage_blocks(base_url: str, maven_repo_url: str | None = None) -> list[UsageBlock]:
    blocks = [
        apt_usage_block(base_url),
        rpm_usage_block(base_url),
        alpine_usage_block(base_url),
        void_usage_block(base_url),
        arch_usage_block(base_url),
    ]

    if maven_repo_url:
        blocks.append(maven_usage_block(maven_repo_url))

    return blocks


def tarminal_usage_blocks(base_url: str) -> list[UsageBlock]:
    return [
        apt_usage_block(base_url),
        rpm_usage_block(base_url),
        alpine_usage_block(base_url),
        void_usage_block(base_url),
        arch_usage_block(base_url),
    ]


def maven_usage_blocks(maven_repo_url: str) -> list[UsageBlock]:
    return [maven_usage_block(maven_repo_url)]