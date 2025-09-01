from __future__ import annotations
import re, os, sys, time, textwrap
from pathlib import Path
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup

try:
    from readability import Document
    HAVE_READABILITY = True
except ImportError:
    HAVE_READABILITY = False

OUT_DIR = Path("app/backend/data/knowledge")

def slugify(url: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9\-]+", "-", urlparse(url).path.strip("/"))
    s = re.sub(r"-+", "-", s).strip("-")
    return s or "page"

def fetch(url: str, timeout: int = 20) -> str:
    headers = {
        "User-Agent": "CW-Challenge-Ingest/1.0 (+nonprod; contact: you@example.com)"
    }
    resp = requests.get(url, headers=headers, timeout=timeout)
    resp.raise_for_status()
    return resp.text

def extract_main(html: str) -> tuple[str, str]:
    if HAVE_READABILITY:
        doc = Document(html)
        title = (doc.short_title() or "").strip()
        article_html = doc.summary(html_partial=True)
        soup = BeautifulSoup(article_html, "html5lib")
    else:
        soup = BeautifulSoup(html, "html5lib")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        candidates = soup.find_all(["article", "main", "section", "div"])
        best = max(candidates, key=lambda el: len(el.get_text(strip=True)), default=soup)
        title_el = soup.find(["h1", "title"])
        title = (title_el.get_text(strip=True) if title_el else "").strip()
        soup = best

    for br in soup.find_all("br"):
        br.replace_with("\n")
    text = soup.get_text(separator="\n", strip=True)

    lines = [re.sub(r"\s+\n", "\n", ln) for ln in text.splitlines()]
    lines = [ln for ln in (ln.strip() for ln in lines) if ln]
    text = "\n".join(lines)

    return title, text

def save_markdown(url: str, title: str, body: str) -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    name = slugify(url)
    if not name.endswith(".md"):
        name = f"{name}.md"
    path = OUT_DIR / name
    content = f"{url}\n\n# {title}\n\n{body}\n"
    path.write_text(content, encoding="utf-8")
    return path

def main(urls: list[str]):
    if not urls:
        print("usage: python tools/ingest_urls.py <url1> <url2> ...")
        sys.exit(2)

    for u in urls:
        try:
            print(f"→ fetching {u}")
            html = fetch(u)
            title, text = extract_main(html)
            if not text:
                print(f"  ! empty content extracted for {u}")
                continue
            path = save_markdown(u, title or "Untitled", text)
            print(f"  ✓ saved to {path}")
            time.sleep(0.8)
        except Exception as e:
            print(f"  ✗ failed: {u}: {type(e).__name__}: {e}")

if __name__ == "__main__":
    main(sys.argv[1:])
