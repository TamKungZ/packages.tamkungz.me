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
