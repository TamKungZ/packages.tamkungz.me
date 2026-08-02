# TamKungZ Package Repository

Static package repository for TamKungZ_ projects. This site is meant for
package managers and developers, not as a product landing page. It serves Linux
package repositories, release metadata, signatures, public keys, and Maven
artifacts.

Maven artifacts are served under `/maven/`:

```gradle
repositories {
    maven {
        name = "TamKungZ Packages"
        url = uri("https://packages.tamkungz.me/maven/")
    }
}
```

## Repository Layout

```text
apt/      Debian/Ubuntu APT repository
rpm/      RPM repository grouped by base architecture
apk/      Alpine APK repository
xbps/     Void Linux XBPS repository
arch/     Arch Linux pacman repository
winget/   Windows Package Manager manifest templates
maven/    Maven-compatible JVM artifact repository
apps/     Human-readable app pages
gpg.key   Public GPG key for signed metadata and artifacts
```

The generated HTML pages are directory indexes for humans. Package managers use
the native metadata files such as `Packages`, `repomd.xml`, `APKINDEX.tar.gz`,
`x86_64-repodata`, pacman databases, and Maven metadata.

## Recommended Setup

1. Create a public GitHub repository, for example `TamKungZ/maven`.
2. Upload this template to the repository root.
3. Go to **Settings > Pages**.
4. Set source to **Deploy from a branch**.
5. Use branch `main` and folder `/ (root)`.
6. Set custom domain to:

```text
packages.tamkungz.me
```

7. In Spaceship DNS, add:

```text
Type: CNAME
Host: packages
Value: TamKungZ.github.io
```

8. After DNS verifies, enable **Enforce HTTPS** in GitHub Pages.

## Files That Matter

```text
CNAME          custom domain for GitHub Pages
.nojekyll      disables Jekyll processing
index.html     landing page for humans
404.html       nicer missing package page
apt/ rpm/ apk/ Linux package repositories
maven/         Maven repository root
```

## Maven Artifact Structure

For:

```gradle
implementation "me.tamkungz:examplelib:1.0.0"
```

The files should look like this:

```text
maven/
  me/
    tamkungz/
      examplelib/
        maven-metadata.xml
        1.0.0/
          examplelib-1.0.0.jar
          examplelib-1.0.0.pom
          examplelib-1.0.0.module
          examplelib-1.0.0-sources.jar
          examplelib-1.0.0.jar.sha1
          examplelib-1.0.0.pom.sha1
```

This template includes only a sample `.pom` and metadata file.
Do not publish the sample as a real dependency unless you also add a real JAR.

## Publishing From A Project

In the actual Java/Gradle project, publish to a local folder first:

```gradle
publishing {
    repositories {
        maven {
            name = "localMaven"
            url = uri(layout.buildDirectory.dir("maven-repo"))
        }
    }
}
```

Then:

```bash
./gradlew publish
```

Copy the generated content from:

```text
build/maven-repo/
```

into `maven/`, commit, and push. The Gradle/Maven output already contains the
group path, for example `me/tamkungz/...` or `org/ex/...`.

## Generate Index Pages

The main entrypoint is:

```bash
python3 scripts/build_site.py
```

It generates Linux package indexes, Maven indexes, `robots.txt`, and
`sitemap.xml`.

## OS And Architecture Coverage

This repository is usable as a static package repository on GitHub Pages or any
plain static host. The Python index generator uses only the Python standard
library, so `python3 scripts/build_site.py` can run on Linux, macOS, and
Windows CI runners.

Linux package installation support has two parts:

```text
distro/package manager = apt, rpm, apk, xbps, pacman
CPU architecture       = amd64/x86_64, arm64/aarch64, etc.
```

The same machine architecture is named differently by different ecosystems:

```text
Generic CPU       Debian/APT   RPM/Fedora   Alpine/APK   Void/XBPS   Arch
x86_64 / amd64    amd64        x86_64       x86_64       x86_64      x86_64
ARM64 / AArch64   arm64        aarch64      aarch64      aarch64     aarch64
ARMv7             armhf        armv7hl      armv7        armv7l      armv7h
```

The repository should only publish an architecture after the project CI has
built a real package for that package manager and architecture. Do not create
empty architecture directories or metadata for packages that do not exist.

The artifacts currently present in this repository cover:

```text
APT:      amd64, arm64 metadata is present
RPM:      x86_64, aarch64 metadata is present
Alpine:   x86_64 metadata is present
Void:     x86_64 metadata is present
Arch:     x86_64 metadata is present
WinGet:   Windows manifests are installer-specific, commonly x64 and arm64
Maven:    JVM artifacts are OS-independent unless the artifact itself is native
```

That means the site itself can be generated from any major CI OS, but the Linux
packages are only installable on the distributions and architectures that have
matching artifacts and native repository metadata.

To expand coverage, build and publish one artifact per target package manager
and architecture, then regenerate each native repository metadata file:

```text
APT:    Packages, Packages.gz, Release, InRelease, Release.gpg
RPM:    repodata/repomd.xml and repodata payload files
Alpine: APKINDEX.tar.gz
Void:   <arch>-repodata
Arch:   tamkungz.db, tamkungz.files
```

WinGet is different from Linux package repositories. A normal public package is
published by submitting YAML manifests to the Microsoft community repository.
This site can host the Windows installer files and keep manifest templates under
`winget/`, but a plain static directory listing is not a WinGet source by
itself. Private WinGet sources require either a pre-indexed source or a REST API
source.

Test a manifest locally before submitting it:

```powershell
winget settings --enable LocalManifestFiles
winget install --manifest winget/manifests/TamKungZ.Example/1.0.0/
```

## CI Publish Example

An example GitHub Actions workflow is available at
`examples/github-actions-publish-packages.yml`. It is intended to live in an
upstream project repository, build release artifacts there, clone this package
repository with a token, copy the artifacts into place, run
`python3 scripts/build_site.py`, then commit and push the generated repository
indexes.

Create a repository secret named `PACKAGES_REPO_TOKEN` with write access to this
package repository, then adapt the package copy paths in the example workflow
for the package formats your project builds. The example uses an architecture
matrix so each Linux package format can map from one generic target to the
architecture name expected by that ecosystem.

## License And Artifact Use

This repository is all rights reserved. It is provided as a public package
repository so compatible tools can download artifacts for building, testing, or
running projects that depend on them.

Do not redistribute, mirror, rehost, modify and redistribute, sell, sublicense,
or claim ownership of artifacts from this repository. Do not use this repository
as the source for unofficial package mirrors.

Individual artifacts may include their own license terms in their POM,
documentation, or distribution page. If an artifact provides separate terms,
those terms apply to that artifact. If no separate license is provided, all
rights are reserved.

## Notes

- Use fixed release versions like `1.0.0`.
- Avoid `+` and `SNAPSHOT` for public docs unless you really need them.
- Keep full app documentation in each app repository or under `/apps/`.
- If traffic gets too high, move the origin to Bunny/Gcore later and keep the same public URL: `https://packages.tamkungz.me/`.
