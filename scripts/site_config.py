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
        "description": "Terms for using TamKungZ_ Packages as a public package repository.",
        "sections": [
            (
                "Repository purpose",
                [
                    "TamKungZ_ Packages is a distribution service for published project artifacts, intended for use with compatible package managers, build tools, and direct downloads.",
                    "You may use this service to install, build, test, or run projects that depend on artifacts published here.",
                ],
            ),
            (
                "Mirrors and redistribution",
                [
                    "Mirroring or redistribution is permitted when performed as part of an official or recognized operating-system distribution, distribution archive, or community package repository, such as repositories maintained by Ubuntu or other established distribution communities.",
                    "Do not create unofficial mirrors, rehost this repository or its artifacts as your own package service, publish them through personal or independently hosted repositories, or otherwise present such redistribution as an official TamKungZ_ Packages source.",
                    "Project-specific license terms still apply to the individual artifacts being mirrored or redistributed.",
                ],
            ),
            (
                "Abuse and automated access",
                [
                    "Do not use this repository for bulk scraping, abusive automation, or traffic that disrupts availability for normal package-manager and download use.",
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
                    "For permission requests, takedown requests, mirror coordination, or repository issues, contact dev@tamkungz.me.",
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
        "description": "License information for TamKungZ_ Packages and the project artifacts distributed through it.",
        "sections": [
            (
                "Repository and distribution service",
                [
                    "TamKungZ_ Packages is a distribution service for project artifacts and repository metadata. It does not replace, modify, or define the license of the projects distributed through it.",
                    "The repository website, generated indexes, metadata, and other repository-specific content are all rights reserved unless stated otherwise.",
                ],
            ),
            (
                "Project and artifact licenses",
                [
                    "Each project or artifact may have its own license terms, provided through its source repository, package metadata, documentation, distribution page, or included license files.",
                    "The license of each project or artifact governs the use, modification, and redistribution of that project or artifact. Availability through TamKungZ_ Packages does not grant additional rights beyond those terms.",
                ],
            ),
            (
                "Mirroring",
                [
                    "Official or recognized operating-system distributions, distribution archives, and community package repositories may mirror artifacts from this service where doing so is compatible with the applicable project or artifact license.",
                    "Unofficial personal mirrors, independently hosted copies, republishing through services such as personal PPAs or similar package hosting, and rehosting presented as an alternative TamKungZ_ Packages repository are not permitted without prior permission.",
                    "A mirror must not imply endorsement, ownership, or official status from TamKungZ_ unless such status has been explicitly granted.",
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
