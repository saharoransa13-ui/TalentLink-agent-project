import asyncio
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse, urldefrag

from playwright.async_api import async_playwright

BASE = "https://www.globalknowledge.com"
CATALOG_URL = f"{BASE}/en-eg/training/courses"
ROOT = Path("data/knowledge_base/technical_resources/globalknowledge/courses")
ROOT.mkdir(parents=True, exist_ok=True)

MAX_CATALOG_PAGES = 120
PAGE_DELAY_MS = 350
COURSE_DELAY_MS = 350

def clean_text(text):
    lines = []
    previous = None
    for line in text.splitlines():
        line = re.sub(r"\s+", " ", line).strip()
        if not line or line == previous:
            continue
        lines.append(line)
        previous = line
    return "\n".join(lines)

def normalize_url(url):
    url, _ = urldefrag(url)
    parsed = urlparse(url)
    return parsed._replace(
        scheme="https",
        netloc="www.globalknowledge.com",
        query=""
    ).geturl().rstrip("/")

def is_course_url(url):
    path = urlparse(url).path.lower()
    return path.startswith("/en-eg/courses/")

def is_catalog_url(url):
    path = urlparse(url).path.lower()
    return (
        path == "/en-eg/training/courses"
        or path.startswith("/en-eg/training/courses/")
        or path.startswith("/en-eg/certifications/")
    )

def safe_filename(url):
    path = urlparse(url).path.rstrip("/")
    slug = path.split("/")[-1] or "course"
    slug = re.sub(r"[^a-zA-Z0-9_-]", "_", slug)
    return slug[:100] + ".md"

async def collect_links(page, url):
    try:
        response = await page.goto(
            url, wait_until="domcontentloaded", timeout=60000
        )
        if not response or response.status >= 400:
            print(f"Catalog HTTP failure: {url}")
            return []
        await page.wait_for_timeout(PAGE_DELAY_MS)
        links = page.locator("a[href]")
        found = []
        for i in range(await links.count()):
            href = await links.nth(i).get_attribute("href")
            if not href:
                continue
            full_url = normalize_url(urljoin(BASE, href))
            if urlparse(full_url).netloc != "www.globalknowledge.com":
                continue
            if is_course_url(full_url) or is_catalog_url(full_url):
                found.append(full_url)
        return found
    except Exception as exc:
        print(f"Catalog error: {url}: {type(exc).__name__}")
        return []

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(locale="en-US")
        page.set_default_timeout(15000)

        print(f"Starting catalog discovery: {CATALOG_URL}")
        queue = [CATALOG_URL]
        visited_catalogs = set()
        course_urls = set()

        while queue and len(visited_catalogs) < MAX_CATALOG_PAGES:
            catalog = queue.pop(0)
            if catalog in visited_catalogs:
                continue
            visited_catalogs.add(catalog)
            print(
                f"[Catalog {len(visited_catalogs)}/"
                f"{MAX_CATALOG_PAGES}] {catalog}"
            )
            found = await collect_links(page, catalog)
            for url in found:
                if is_course_url(url):
                    course_urls.add(url)
                elif is_catalog_url(url) and url not in visited_catalogs:
                    if url not in queue:
                        queue.append(url)

        print(f"\nUnique course URLs discovered: {len(course_urls)}")
        print(f"Catalog pages visited: {len(visited_catalogs)}")

        saved = 0
        failed = 0
        ordered_urls = sorted(course_urls)

        for number, url in enumerate(ordered_urls, start=1):
            output = ROOT / safe_filename(url)

            if output.exists() and output.stat().st_size > 500:
                print(f"[{number}/{len(ordered_urls)}] Already saved: {output.name}")
                saved += 1
                continue

            try:
                response = await page.goto(
                    url, wait_until="domcontentloaded", timeout=60000
                )
                await page.wait_for_timeout(COURSE_DELAY_MS)

                if not response or response.status < 200 or response.status >= 400:
                    print(f"[{number}/{len(ordered_urls)}] HTTP failure: {url}")
                    failed += 1
                    continue

                main = page.locator("main").first
                if await main.count():
                    text = await main.inner_text()
                else:
                    text = await page.locator("body").inner_text()

                text = clean_text(text)
                if len(text) < 250:
                    print(f"[{number}/{len(ordered_urls)}] Too little text: {url}")
                    failed += 1
                    continue

                title = await page.title()
                content = (
                    f"# {title or url}\n\n"
                    f"- Source: Global Knowledge\n"
                    f"- Course URL: {url}\n"
                    f"- Retrieved UTC: {datetime.now(timezone.utc).isoformat()}\n"
                    f"- Note: Course schedules, prices, and availability can change. "
                    f"Verify current details on the source page.\n\n"
                    f"## Course details\n\n{text}\n"
                )
                output.write_text(content, encoding="utf-8")
                saved += 1
                print(f"[{number}/{len(ordered_urls)}] Saved: {output.name}")

            except Exception as exc:
                failed += 1
                print(
                    f"[{number}/{len(ordered_urls)}] Failed: {url}: "
                    f"{type(exc).__name__}: {exc}"
                )

        await browser.close()

    print("\nScrape finished.")
    print(f"Catalog pages visited: {len(visited_catalogs)}")
    print(f"Unique course URLs discovered: {len(course_urls)}")
    print(f"Files saved or already present: {saved}")
    print(f"Failed or skipped: {failed}")
    print(f"Output folder: {ROOT.resolve()}")
    print("No RAG ingestion was performed.")

asyncio.run(main())
