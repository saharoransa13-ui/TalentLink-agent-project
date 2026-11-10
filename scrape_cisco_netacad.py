import asyncio
from pathlib import Path
from datetime import datetime, timezone
from playwright.async_api import async_playwright

ROOT = Path("data/knowledge_base/technical_resources/cisco_netacad")
ROOT.mkdir(parents=True, exist_ok=True)

PAGES = [
    ("networking_basics", "https://www.netacad.com/courses/networking-basics/how-routers-work?courseLang=en-US"),
    ("networking_essentials", "https://www.netacad.com/courses/networking-essentials/1000?courseLang=en-US"),
    ("networking_devices_initial_configuration", "https://www.netacad.com/courses/networking-devices-and-initial-configuration?courseLang=en-US"),
]

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(locale="en-US")

        try:
            for slug, url in PAGES:
                print(f"\nFetching: {url}")
                try:
                    response = await page.goto(
                        url, wait_until="domcontentloaded", timeout=60000
                    )
                    await page.wait_for_timeout(5000)

                    status = response.status if response else 0
                    print("HTTP status:", status)

                    if status < 200 or status >= 400:
                        print("Skipped: unsuccessful HTTP response.")
                        continue

                    title = await page.title()
                    body = page.locator("body")
                    text = await body.inner_text(timeout=15000)
                    text = "\n".join(
                        line.strip() for line in text.splitlines() if line.strip()
                    )

                    if len(text) < 500:
                        print(f"Skipped: insufficient visible text ({len(text)} chars).")
                        continue

                    output = ROOT / f"{slug}.md"
                    output.write_text(
                        f"# {title}\n\n"
                        f"- Source: Cisco Networking Academy\n"
                        f"- Original URL: {url}\n"
                        f"- Retrieved UTC: {datetime.now(timezone.utc).isoformat()}\n"
                        f"- Content type: Public course-page extract; not full lesson content\n\n"
                        f"## Extracted page text\n\n{text}\n",
                        encoding="utf-8",
                    )
                    print(f"Saved: {output} | {len(text)} characters")

                except Exception as exc:
                    print(f"Failed: {type(exc).__name__}: {exc}")

        finally:
            await browser.close()

    print(f"\nOutput folder: {ROOT.resolve()}")

asyncio.run(main())
