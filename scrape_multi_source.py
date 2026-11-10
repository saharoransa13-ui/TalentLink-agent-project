import asyncio
import re
from datetime import datetime, timezone
from pathlib import Path
from playwright.async_api import async_playwright

ROOT = Path("data/knowledge_base/technical_resources/multi_source")
ROOT.mkdir(parents=True, exist_ok=True)

PAGES = [
    {
        "source": "Microsoft Learn",
        "slug": "powershell_getting_started",
        "url": "https://learn.microsoft.com/en-us/powershell/scripting/learn/ps101/00-introduction",
    },
    {
        "source": "Microsoft Learn",
        "slug": "windows_server_dns",
        "url": "https://learn.microsoft.com/en-us/windows-server/networking/dns/dns-top",
    },
    {
        "source": "Microsoft Learn",
        "slug": "windows_server_dhcp",
        "url": "https://learn.microsoft.com/en-us/windows-server/networking/technologies/dhcp/dhcp-top",
    },
    {
        "source": "Ansible",
        "slug": "ansible_playbooks",
        "url": "https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_intro.html",
    },
    {
        "source": "Ansible",
        "slug": "ansible_inventory",
        "url": "https://docs.ansible.com/ansible/latest/inventory_guide/intro_inventory.html",
    },
]

NOISE = {
    "Skip to main content",
    "Skip to content",
    "Search",
    "Search the documentation",
    "Sign in",
    "Sign out",
    "English",
    "Privacy",
    "Terms of use",
    "Trademarks",
    "© Microsoft",
}

def clean_text(text):
    lines = []
    seen = set()

    for line in text.splitlines():
        line = re.sub(r"\s+", " ", line).strip()
        if not line or line in NOISE:
            continue
        if line in seen:
            continue
        seen.add(line)
        lines.append(line)

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
                slug = item["slug"]
                url = item["url"]
                print(f"\nFetching {item['source']}: {url}")

                saved = False

                for attempt in range(1, 4):
                    try:
                        response = await page.goto(
                            url,
                            wait_until="domcontentloaded",
                            timeout=60000,
                        )
                        await page.wait_for_timeout(2500)

                        status = response.status if response else 0
                        print(f"Attempt {attempt} | HTTP {status}")

                        if not response or status < 200 or status >= 400:
                            continue

                        # Prefer the main article instead of the full navigation shell.
                        locator = page.locator(
                            "main, [role='main'], #main"
                        ).first

                        if await locator.count():
                            text = await locator.inner_text(timeout=10000)
                        else:
                            text = await page.locator("body").inner_text(
                                timeout=10000
                            )

                        text = clean_text(text)

                        if len(text) < 800:
                            print(
                                f"Skipped attempt: only {len(text)} useful characters."
                            )
                            continue

                        title = await page.title()
                        output = ROOT / f"{slug}.md"

                        content = (
                            f"# {title}\n\n"
                            f"- Source: {item['source']}\n"
                            f"- Original URL: {url}\n"
                            f"- Retrieved UTC: "
                            f"{datetime.now(timezone.utc).isoformat()}\n"
                            f"- Content type: Public documentation page extract\n\n"
                            f"## Extracted documentation text\n\n{text}\n"
                        )

                        output.write_text(content, encoding="utf-8")
                        print(
                            f"Saved: {output} | "
                            f"{len(text)} characters"
                        )
                        saved = True
                        break

                    except Exception as exc:
                        print(
                            f"Attempt {attempt} failed: "
                            f"{type(exc).__name__}: {exc}"
                        )

                if not saved:
                    print(
                        f"Not saved: {slug}. "
                        "The page may require different extraction handling."
                    )

        finally:
            await browser.close()

    print(f"\nFinished. Output folder: {ROOT.resolve()}")
    print("No RAG ingestion was performed.")

asyncio.run(main())

