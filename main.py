import asyncio
import json
import sys
from pathlib import Path
from urllib.parse import urlencode

from lxml import html
from playwright.async_api import async_playwright
from playwright.async_api._generated import Browser, BrowserContext

from json_validator import validate


async def try_proxy_on_github(browser: Browser, in_proxy): # pragma: no cover
    context: BrowserContext | None = None
    try:
        context = await browser.new_context(proxy={"server": f"http://{in_proxy}"})
        page = await context.new_page()
        await page.goto(f"https://github.com", wait_until="domcontentloaded", timeout=5000)
        print(f"Using proxy {in_proxy}")
        return context
    except Exception as e:
        print(f"Failed with proxy {in_proxy}: {e}")

        if context:
            await context.close()

        return None

async def get_working_context(browser: Browser, proxies): # pragma: no cover
    tasks = [asyncio.create_task(try_proxy_on_github(browser, proxy_from_json)) for proxy_from_json in proxies]

    context = None
    for task in asyncio.as_completed(tasks):
        context = await task
        if context:
            break

    if not context:
        sys.exit("No working proxies found")

    # Cancel remaining tasks
    for t in tasks:
        if not t.done():
            t.cancel()
    contexts_to_close = [br_context for br_context in browser.contexts if br_context is not context]
    for br_context in contexts_to_close:
        await br_context.close()

    return context

async def get_html(context: BrowserContext, url: str, retries: int = 3, delay: float = 1.0) -> str:  # pragma: no cover
    page = context.pages[0]
    for attempt in range(retries):
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=5000)
            return await page.content()
        except Error as e:
            print(f"Attempt {attempt+1} failed: {e}")
            if attempt < retries - 1:
                await asyncio.sleep(delay)
            else:
                raise

    return ""

def parse_search_results(html_string: str):
    html_parser = html.fromstring(html_string)
    a_tags = html_parser.xpath("//div[contains(@class,'search-title')]//a")
    urls = [{"url": "https://github.com" + a.get('href')} for a in a_tags if a.get('href')]

    return urls

def parse_extras(extra_html):
    result = {"extra": {}}

    repo_tree = html.fromstring(extra_html)
    owner_crumb = repo_tree.xpath('//*[@itemprop="author"]/a/text()')
    owner_name = owner_crumb[0] if owner_crumb else None
    if not owner_name:
        raise IndexError("No owner name found")

    result["extra"]["owner"] = owner_name.strip() if owner_name else None

    ul = repo_tree.xpath('//div[contains(@class,"BorderGrid-row")][.//h2[text()="Languages"]]//ul')
    ul = ul[0] if ul else None

    if ul is None:
        result["extra"]["language_stats"] = None
        return result

    for li in ul.xpath('./li'):
        span_texts: tuple[str, str] = li.xpath('.//span/text()')
        result["extra"].setdefault("language_stats", {})[span_texts[0]] = span_texts[1].rstrip("%")

    return result

async def main(): # pragma: no cover
    json_data = validate(Path("input.json"))
    params = {
        "q": " ".join(json_data["keywords"]),
        "type": json_data["type"]
    }

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        context = await get_working_context(browser, json_data["proxies"])
        search_result_html = await get_html(context, f"https://github.com/search?{urlencode(params)}")
        urls = parse_search_results(search_result_html)
        if params["type"].lower() == "repositories":
            for url in urls:
                extra_html = await get_html(context, url["url"])
                parsed_extra = parse_extras(extra_html)
                url.update(parsed_extra)

        await browser.close()

    with open("output.json", "w") as f:
        json.dump(urls, f, indent=4)

    print(json.dumps(urls, indent=4))

if __name__ == "__main__":
    asyncio.run(main()) # pragma: no cover
