from pathlib import Path
from html import escape
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent

IGNORE_DIRS = {
    ".git", ".github", "scripts", "examples"
}

IGNORE_FILES = {
    "index.html"
}

def should_skip_dir(path: Path) -> bool:
    return any(part in IGNORE_DIRS for part in path.parts)

def rel_url(path: Path, base: Path) -> str:
    return escape(path.relative_to(base).as_posix())

def make_index(directory: Path):
    items = []

    if directory != ROOT:
        items.append(('dir', '..', '../'))

    for child in sorted(directory.iterdir(), key=lambda p: (p.is_file(), p.name.lower())):
        if child.name in IGNORE_FILES:
            continue
        if child.name.startswith(".") and child.name not in {".nojekyll"}:
            continue
        if child.is_dir() and child.name in IGNORE_DIRS:
            continue

        name = child.name + ("/" if child.is_dir() else "")
        href = escape(child.name + ("/" if child.is_dir() else ""))
        kind = "dir" if child.is_dir() else "file"
        size = "" if child.is_dir() else f"{child.stat().st_size:,} bytes"

        items.append((kind, name, href, size))

    title = "/" if directory == ROOT else "/" + directory.relative_to(ROOT).as_posix() + "/"

    rows = []
    for item in items:
        if item[0] == "dir" and item[1] == "..":
            rows.append(f'<tr><td>📁</td><td><a href="{item[2]}">../</a></td><td></td></tr>')
        else:
            kind, name, href, size = item
            icon = "📁" if kind == "dir" else "📄"
            rows.append(f'<tr><td>{icon}</td><td><a href="{href}">{escape(name)}</a></td><td>{escape(size)}</td></tr>')

    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>TamKungZ Maven Repository - {escape(title)}</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    body {{
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      margin: 40px;
      background: #0f0f0f;
      color: #e8e8e8;
    }}
    a {{ color: #9fc3fc; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    table {{ border-collapse: collapse; width: 100%; max-width: 1000px; }}
    td {{ padding: 6px 10px; border-bottom: 1px solid #2a2a2a; }}
    .path {{ color: #aaa; margin-bottom: 24px; }}
    .usage {{
      margin: 24px 0;
      padding: 16px;
      background: #181818;
      border: 1px solid #333;
      border-radius: 8px;
      max-width: 1000px;
      white-space: pre-wrap;
    }}
  </style>
</head>
<body>
  <h1>TamKungZ Maven Repository</h1>
  <div class="path">{escape(title)}</div>

  <div class="usage">repositories {{
    maven {{
        name = "TamKungZ Maven"
        url = uri("https://maven.tamkungz.me/")
    }}
}}</div>

  <table>
    <tbody>
      {"".join(rows)}
    </tbody>
  </table>

  <p style="margin-top:32px;color:#777">
    Generated at {datetime.utcnow().isoformat()}Z
  </p>
</body>
</html>
"""
    (directory / "index.html").write_text(html, encoding="utf-8")

def main():
    for directory in ROOT.rglob("*"):
        if directory.is_dir() and not should_skip_dir(directory.relative_to(ROOT)):
            make_index(directory)

    make_index(ROOT)

if __name__ == "__main__":
    main()