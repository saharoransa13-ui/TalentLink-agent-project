import asyncio
from playwright.async_api import async_playwright

URL = "https://learn.microsoft.com/en-us/windows-server/"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(locale="en-US")
        try:
            response = await page.goto(
                URL, wait_until="domcontentloaded", timeout=60000
            )
            await page.wait_for_timeout(4000)

            print("HTTP:", response.status if response else "No response")
            print("TITLE:", await page.title())
            print("URL:", page.url)

            for selector in [
                "main", "article", "[role='main']",
                "#main", ".content", "body"
            ]:
                locator = page.locator(selector).first
                try:
                    if await locator.count():
                        text = await locator.inner_text(timeout=8000)
                        print(f"\n--- {selector}: {len(text)} characters ---")
                        print(text[:1200].replace("\n", " "))
                except Exception as exc:
                    print(f"{selector}: {type(exc).__name__}")

        finally:
            await browser.close()

asyncio.run(main())
