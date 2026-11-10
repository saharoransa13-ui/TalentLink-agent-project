import asyncio
import re
from datetime import datetime, timezone
from pathlib import Path
from playwright.async_api import async_playwright

ROOT = Path("data/knowledge_base/technical_resources/fastlane")
ROOT.mkdir(parents=True, exist_ok=True)

PAGES = [
    {
        "slug": "fastlane_home",
        "url": "https://www.fastlanemea.com/",
    },
    {
        "slug": "fastlane_training_vendors",
        "url": "https://www.fastlanemea.com/training",
    },
    {
        "slug": "fastlane_online_course_catalog",
        "url": "https://www.fastlanemea.com/ilocourses",
    },
]

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

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(
            locale="en-US",
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/131.0.0.0 Safari/537.36"
            ),
        )

        try:
            for item in PAGES:
                url = item["url"]
                slug = item["slug"]
                print(f"\nFetching Fast Lane MENA: {url}")
                saved = False

                for attempt in range(1, 4):
                    try:
                        response = await page.goto(
                            url,
                            wait_until="domcontentloaded",
                            timeout=60000,
                        )
                        await page.wait_for_timeout(3000)
                        status = response.status if response else 0
                        print(f"Attempt {attempt} | HTTP {status}")

                        if not response or status < 200 or status >= 400:
                            continue

                        locator = page.locator(
                            "main, [role='main'], #main"
                        ).first
                        if await locator.count():
                            text = await locator.inner_text(timeout=15000)
                        else:
                            text = await page.locator("body").inner_text(
                                timeout=15000
                            )

                        text = clean_text(text)
                        if len(text) < 500:
                            print(f"Skipped: only {len(text)} characters.")
                            continue

                        title = await page.title()
                        output = ROOT / f"{slug}.md"
                        content = (
                            f"# {title}\n\n"
                            f"- Source: Fast Lane MENA\n"
                            f"- Original URL: {url}\n"
                            f"- Retrieved UTC: "
                            f"{datetime.now(timezone.utc).isoformat()}\n"
                            f"- Content type: Public website extract; "
                            f"course schedules may change\n\n"
                            f"## Extracted website text\n\n{text}\n"
                        )
                        output.write_text(content, encoding="utf-8")
                        print(f"Saved: {output} | {len(text)} characters")
                        saved = True
                        break

                    except Exception as exc:
                        print(
                            f"Attempt {attempt} failed: "
                            f"{type(exc).__name__}: {exc}"
                        )

                if not saved:
                    print(f"Not saved: {slug}")

        finally:
            await browser.close()

    print(f"\nFinished. Output folder: {ROOT.resolve()}")
    print("No RAG ingestion was performed.")

asyncio.run(main())
