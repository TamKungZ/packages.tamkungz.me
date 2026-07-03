# TamKungZ Maven Repository

Static Maven repository template for:

```gradle
repositories {
    maven {
        name = "TamKungZ Maven"
        url = uri("https://maven.tamkungz.me/")
    }
}
```

## Recommended setup

1. Create a public GitHub repository, for example `TamKungZ/maven`.
2. Upload this template to the repository root.
3. Go to **Settings > Pages**.
4. Set source to **Deploy from a branch**.
5. Use branch `main` and folder `/ (root)`.
6. Set custom domain to:

```text
maven.tamkungz.me
```

7. In Spaceship DNS, add:

```text
Type: CNAME
Host: maven
Value: TamKungZ.github.io
```

8. After DNS verifies, enable **Enforce HTTPS** in GitHub Pages.

## Files that matter

```text
CNAME        custom domain for GitHub Pages
.nojekyll    disables Jekyll processing
index.html   landing page for humans
404.html     nicer missing artifact page
me/          Maven group path starts here
```

## Maven artifact structure

For:

```gradle
implementation "me.tamkungz:examplelib:1.0.0"
```

The files should look like this:

```text
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

## Publishing from a project

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

into this repository root, commit, and push.

## Notes

- Use fixed release versions like `1.0.0`.
- Avoid `+` and `SNAPSHOT` for public docs unless you really need them.
- Keep this repository mostly Maven files. Put full documentation on another site, for example `repo.tamkungz.me`.
- If traffic gets too high, move the origin to Bunny/Gcore later and keep the same public URL: `https://maven.tamkungz.me/`.
