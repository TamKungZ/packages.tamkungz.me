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
FAVICON_SVG_URL = "/favicon-20260714.svg"
FAVICON_ICO_URL = "/favicon-20260714.ico"
THEME_COLOR = "#03983d"

# --- Author / SEO identity ---------------------------------------------

AUTHOR_NAME = "TamKungZ_"
AUTHOR_TWITTER_HANDLE = "@TamKungZ_"
AUTHOR_EMAIL = "dev@tamkungz.me"
AUTHOR_GITHUB_URL = "https://github.com/TamKungZ"

# --- Repository layout ---------------------------------------------------

# Root-level package repository layout. release.yml currently publishes
# apt/rpm/apk/xbps/arch/apps; JVM artifacts live under /maven.
# /apt              APT repository shared by all Debian packages
# /rpm/<basearch>   RPM repository shared by all RPM packages
# /apk/<arch>       Alpine APK repository
# /xbps/<arch>      Void Linux XBPS repository
# /arch/<arch>      Arch Linux pacman repository
# /maven            Maven repository
# /apps/<app>       human-readable product pages only
PROJECT_ROOTS = {
    "apt",
    "rpm",
    "apk",
    "xbps",
    "arch",
    "maven",
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
    "favicon.svg",
    "favicon.ico",
    "favicon-20260714.svg",
    "favicon-20260714.ico",
}

# --- Legal pages ---------------------------------------------------------

LegalPage = dict[str, object]

LEGAL_PAGES: list[LegalPage] = [
    {
        "slug": "terms",
        "title": "Terms of Use",
        "description": "Terms for using TamKungZ_ Packages as a public package repository.",
        "sections": [
            (
                "Repository purpose",
                [
                    "TamKungZ_ Packages is provided as a public package repository for compatible package managers, build tools, and users downloading published project artifacts.",
                    "You may use this service to install, build, test, or run projects that depend on artifacts published here.",
                ],
            ),
            (
                "Restrictions",
                [
                    "Do not redistribute, mirror, rehost, modify and redistribute, sell, sublicense, or claim ownership of artifacts from this repository unless a specific artifact license allows it.",
                    "Do not use this repository as the source for unofficial package mirrors, bulk scraping, abusive automation, or traffic that disrupts availability for normal package-manager use.",
                ],
            ),
            (
                "Availability",
                [
                    "This service is provided as-is, without uptime, compatibility, support, or warranty guarantees.",
                    "Artifacts, metadata, repository paths, and signing keys may change when needed for maintenance, security, or release management.",
                ],
            ),
            (
                "Contact",
                [
                    "For permission requests, takedown requests, or repository issues, contact dev@tamkungz.me.",
                ],
            ),
        ],
    },
    {
        "slug": "privacy",
        "title": "Privacy Policy",
        "description": "Privacy notes for visitors and package-manager clients using TamKungZ_ Packages.",
        "sections": [
            (
                "Data collected",
                [
                    "This site does not provide user accounts, comments, or payment forms.",
                    "Normal web server, CDN, hosting, and security logs may record request metadata such as IP address, user agent, requested URL, referrer, status code, and timestamp.",
                ],
            ),
            (
                "Analytics",
                [
                    "Generated package index pages include the Ahrefs analytics script to understand aggregate site traffic.",
                    "Package managers and automated clients may also appear in server or analytics logs when they request repository metadata or artifacts.",
                ],
            ),
            (
                "Use of data",
                [
                    "Operational data is used to maintain the repository, investigate abuse, debug availability problems, and understand aggregate usage.",
                    "This site does not intentionally sell personal information.",
                ],
            ),
            (
                "Contact",
                [
                    "For privacy questions or removal requests, contact dev@tamkungz.me.",
                ],
            ),
        ],
    },
    {
        "slug": "license",
        "title": "License and Artifact Use",
        "description": "License terms for this package repository and published artifacts.",
        "sections": [
            (
                "Repository license",
                [
                    "This package repository is all rights reserved unless stated otherwise.",
                    "You are allowed to download artifacts through compatible package managers or build tools for building, testing, installing, or running projects that depend on them.",
                ],
            ),
            (
                "Artifact licenses",
                [
                    "Individual artifacts may include their own license terms in their POM, package metadata, documentation, source repository, or distribution page.",
                    "If an artifact provides separate terms, those terms apply to that artifact. If no separate license is provided, all rights are reserved.",
                ],
            ),
            (
                "Redistribution",
                [
                    "Do not redistribute, mirror, rehost, modify and redistribute, sell, sublicense, or claim ownership of repository artifacts unless the artifact's own license explicitly permits it.",
                ],
            ),
        ],
    },
]

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
