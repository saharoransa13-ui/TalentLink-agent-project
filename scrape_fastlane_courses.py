import asyncio
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse

from playwright.async_api import async_playwright

BASE = "https://www.fastlanemea.com"
CATALOG_URL = f"{BASE}/ilocourses"
ROOT = Path("data/knowledge_base/technical_resources/fastlane/courses")
ROOT.mkdir(parents=True, exist_ok=True)

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

def safe_filename(url):
    slug = urlparse(url).path.rstrip("/").split("/")[-1]
    return re.sub(r"[^a-zA-Z0-9_-]", "_", slug) + ".md"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(locale="en-US")

        print("Discovering course URLs...")
        await page.goto(
            CATALOG_URL,
            wait_until="domcontentloaded",
            timeout=60000,
        )
        await page.wait_for_timeout(2000)

        links = page.locator("[role='main'] a")
        courses = {}

        for i in range(await links.count()):
            link = links.nth(i)
            title = " ".join((await link.inner_text()).split())
            href = await link.get_attribute("href")
            if not title or not href:
                continue

            full_url = urljoin(BASE, href)
            parsed = urlparse(full_url)
            if (
                parsed.netloc == urlparse(BASE).netloc
                and parsed.path.startswith("/course/")
            ):
                courses[parsed.path] = {
                    "title": title,
                    "url": f"{BASE}{parsed.path}",
                }

        print(f"Found {len(courses)} unique course pages.")
        saved = 0
        failed = 0

        for number, item in enumerate(courses.values(), start=1):
            output = ROOT / safe_filename(item["url"])

            if output.exists() and output.stat().st_size > 500:
                print(f"[{number}/{len(courses)}] Already saved: {output.name}")
                saved += 1
                continue

            try:
                response = await page.goto(
                    item["url"],
                    wait_until="domcontentloaded",
                    timeout=60000,
                )
                await page.wait_for_timeout(800)

                if not response or response.status < 200 or response.status >= 400:
                    print(f"[{number}/{len(courses)}] HTTP failure: {item['url']}")
                    failed += 1
                    continue

                main = page.locator("[role='main']").first
                if await main.count():
                    text = await main.inner_text(timeout=15000)
                else:
                    text = await page.locator("body").inner_text(timeout=15000)

                text = clean_text(text)
                if len(text) < 300:
                    print(f"[{number}/{len(courses)}] Too little text: {item['url']}")
                    failed += 1
                    continue

                title = await page.title()
                content = (
                    f"# {title or item['title']}\n\n"
                    f"- Source: Fast Lane MENA\n"
                    f"- Course URL: {item['url']}\n"
                    f"- Retrieved UTC: {datetime.now(timezone.utc).isoformat()}\n"
                    f"- Note: Course prices and schedules may change; "
                    f"verify details on the source page.\n\n"
                    f"## Course details\n\n{text}\n"
                )
                output.write_text(content, encoding="utf-8")
                saved += 1
                print(f"[{number}/{len(courses)}] Saved: {output.name}")

            except Exception as exc:
                failed += 1
                print(
                    f"[{number}/{len(courses)}] Failed: "
                    f"{type(exc).__name__}: {exc}"
                )

            await page.wait_for_timeout(700)

        await browser.close()

    print("\nScrape finished.")
    print(f"Course pages discovered: {len(courses)}")
    print(f"Files saved or already present: {saved}")
    print(f"Failed or skipped: {failed}")
    print(f"Output folder: {ROOT.resolve()}")
    print("No RAG ingestion was performed.")

asyncio.run(main())
