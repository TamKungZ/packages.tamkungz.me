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
# apt/rpm/apk/xbps/arch; JVM artifacts live under /maven.
# App landing pages moved to https://dev.tamkungz.me/projects/.
# Do not generate /apps pages here anymore.
# /apt              APT repository shared by all Debian packages
# /rpm/<basearch>   RPM repository shared by all RPM packages
# /apk/<arch>       Alpine APK repository
# /xbps/<arch>      Void Linux XBPS repository
# /arch/<arch>      Arch Linux pacman repository
# /maven            Maven repository
# /winget           Windows Package Manager manifest templates
PROJECT_ROOTS = {
    "apt",
    "rpm",
    "apk",
    "xbps",
    "arch",
    "maven",
    "winget",
}

IGNORE_DIRS = {
    ".git",
    ".github",
    "scripts",
    "apps",
    "examples",
    "resources",
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
        "description": "Terms for using TamKungZ_ Packages.",
        "sections": [
            (
                "Repository purpose",
                [
                    "TamKungZ_ Packages is a package repository used to host packages and release artifacts published by TamKungZ_ for easier installation and download.",
                    "You may use this repository with supported package managers and build tools to download, install, update, build, test, or use packages published here.",
                ],
            ),
            (
                "Mirrors",
                [
                    "Mirroring is allowed for official distribution repositories and established community package repositories, such as repositories maintained by Ubuntu or other Linux distribution communities.",
                    "Do not create or publish unofficial personal mirrors, PPAs, Launchpad repositories, or independently hosted copies of this repository without permission.",
                    "A mirror must not be presented as an official TamKungZ_ repository unless it is maintained or approved by TamKungZ_.",
                ],
            ),
            (
                "Repository use",
                [
                    "Do not use this repository for abusive scraping, excessive automated requests, or other activity that disrupts normal package downloads and package-manager access.",
                ],
            ),
            (
                "Availability",
                [
                    "This repository is provided as-is without uptime, compatibility, support, or warranty guarantees.",
                    "Packages, metadata, repository paths, and signing keys may change when needed for maintenance, security, or releases.",
                ],
            ),
            (
                "Contact",
                [
                    "For mirror requests, takedown requests, permissions, or repository issues, contact dev@tamkungz.me.",
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
        "description": "License information for this repository and the projects published through it.",
        "sections": [
            (
                "Repository",
                [
                    "TamKungZ_ Packages is a package hosting repository. It provides packages, release files, repository metadata, and related files for download and installation.",
                    "The repository itself does not determine the license of the projects or packages published through it.",
                ],
            ),
            (
                "Project licenses",
                [
                    "Projects and packages published here may have their own licenses.",
                    "The license provided by each project applies to that project's source code, binaries, packages, and other artifacts as specified by that license.",
                    "Publishing a project through TamKungZ_ Packages does not replace or change the project's own license.",
                ],
            ),
            (
                "Mirroring",
                [
                    "Official distribution repositories and established community package repositories may mirror packages from this repository when permitted by the applicable project license.",
                    "Do not create unofficial personal mirrors, PPAs, Launchpad repositories, or independently hosted copies of this repository without permission.",
                    "Mirroring does not transfer ownership of the packages, projects, repository metadata, names, or branding.",
                ],
            ),
        ],
    },
]

# --- Remote README sources -------------------------------------------

# App landing pages used to live under /apps/<name> on the package site.
# Those pages now live on dev.tamkungz.me/projects, so these README sources
# are kept only for package-directory summaries if reused later.
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


def apt_usage_block(
    base_url: str,
    package_name: str = "<package-name>",
    architectures: str = "amd64,arm64",
) -> UsageBlock:
    return (
        "Debian / Ubuntu / Zorin",
        "bash",
        f"""curl -fsSL {base_url}/gpg.key | \\
  sudo gpg --dearmor -o /usr/share/keyrings/tamkungz-packages.gpg

echo "deb [arch={architectures} signed-by=/usr/share/keyrings/tamkungz-packages.gpg] {base_url}/apt stable main" | \\
  sudo tee /etc/apt/sources.list.d/tamkungz-packages.list

sudo apt update
sudo apt install {package_name}""",
    )


def rpm_usage_block(base_url: str, package_name: str = "<package-name>") -> UsageBlock:
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

sudo dnf install {package_name}""",
    )


def alpine_usage_block(base_url: str, package_name: str = "<package-name>") -> UsageBlock:
    return (
        "Alpine APK",
        "bash",
        f"""sudo mkdir -p /etc/apk/keys
curl -fsSL {base_url}/apk/tamkungz.rsa.pub | \\
  sudo tee /etc/apk/keys/tamkungz.rsa.pub >/dev/null

echo "{base_url}/apk/$(apk --print-arch)" | \\
  sudo tee -a /etc/apk/repositories

sudo apk update
sudo apk add {package_name}""",
    )


def void_usage_block(base_url: str, package_name: str = "<package-name>") -> UsageBlock:
    return (
        "Void XBPS",
        "bash",
        f"""sudo mkdir -p /etc/xbps.d
sudo tee /etc/xbps.d/tamkungz.conf >/dev/null <<'EOF'
repository={base_url}/xbps/x86_64
EOF

sudo xbps-install -S
sudo xbps-install {package_name}""",
    )


def arch_usage_block(base_url: str, package_name: str = "<package-name>") -> UsageBlock:
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
sudo pacman -S {package_name}""",
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


def winget_usage_block(package_id: str = "TamKungZ.<PackageName>") -> UsageBlock:
    return (
        "Windows Package Manager",
        "powershell",
        f"""# repo.tamkungz.me: private WinGet REST source
winget source add --name tamkungz --arg https://repo.tamkungz.me/winget --type Microsoft.Rest
winget install --id {package_id} -e

# packages.tamkungz.me: static manifests for local testing/submission
winget settings --enable LocalManifestFiles
winget install --manifest winget/manifests/{package_id}/<version>/""",
    )


def root_usage_blocks(base_url: str, maven_repo_url: str | None = None) -> list[UsageBlock]:
    blocks = [
        apt_usage_block(base_url),
        rpm_usage_block(base_url),
        alpine_usage_block(base_url),
        void_usage_block(base_url),
        arch_usage_block(base_url),
        winget_usage_block(),
    ]

    if maven_repo_url:
        blocks.append(maven_usage_block(maven_repo_url))

    return blocks


def tarminal_usage_blocks(base_url: str) -> list[UsageBlock]:
    return [
        apt_usage_block(base_url, package_name="tarminal", architectures="amd64"),
        rpm_usage_block(base_url, package_name="tarminal"),
        alpine_usage_block(base_url, package_name="tarminal"),
        void_usage_block(base_url, package_name="tarminal"),
        arch_usage_block(base_url, package_name="tarminal"),
    ]


def maven_usage_blocks(maven_repo_url: str) -> list[UsageBlock]:
    return [maven_usage_block(maven_repo_url)]
