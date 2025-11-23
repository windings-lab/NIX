import asyncio
import json
import sys
from pathlib import Path
from urllib.parse import urlencode

from lxml import html
from playwright.async_api import async_playwright
from playwright.async_api._generated import Browser

from json_validator import validate

async def search_on_github(browser: Browser, params, proxies):
    async def process(in_proxy):
        context = None
        try:
            context = await browser.new_context(proxy={"server": f"http://{in_proxy}"})
            page = await context.new_page()
            await page.goto(f"https://github.com/search?{urlencode(params)}",
                            wait_until="domcontentloaded", timeout=5000)
            result_html = await page.content()
            return context, page, result_html
        except Exception as e:
            print(f"Failed with proxy {in_proxy}: {e}")

            if context:
                await context.close()

            return None, None, None

    tasks = [asyncio.create_task(process(proxy_from_json)) for proxy_from_json in proxies]

    result = (None, None, None)
    context = None
    for task in asyncio.as_completed(tasks):
        context, page, result_html = await task
        if result_html:
            result = (context, page, result_html)
            break

    if not result[0]:
        sys.exit("No working proxies found")

    # Cancel remaining tasks
    for t in tasks:
        if not t.done():
            t.cancel()

    contexts_to_close = [br_context for br_context in browser.contexts if br_context is not context]
    for br_context in contexts_to_close:
        await br_context.close()

    return result

def parsing_search_results(html_string: str):
    html_parser = html.fromstring(html_string)
    a_tags = html_parser.xpath("//div[contains(@class,'search-title')]//a")
    urls = [{"url": "https://github.com" + a.get('href')} for a in a_tags if a.get('href')]

    return urls

async def main():
    json_data = validate(Path("input.json"))
    params = {
        "q": " ".join(json_data["keywords"]),
        "type": json_data["type"]
    }

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context, page, html_string = await search_on_github(browser, params, json_data["proxies"])

        urls = parsing_search_results(html_string)

        if params["type"].lower() == "repositories":
            for url in urls:
                await page.goto(
                    url["url"],
                    wait_until="domcontentloaded",
                )
                repo_html = await page.content()
                repo_tree = html.fromstring(repo_html)
                owner_crumb = repo_tree.xpath('//*[@itemprop="author"]/a/text()')
                owner_name = owner_crumb[0] if owner_crumb else None
                url.setdefault("extra", {})["owner"] = owner_name.strip()

                ul = repo_tree.xpath('//div[contains(@class,"BorderGrid-row")][.//h2[text()="Languages"]]//ul')
                ul = ul[0] if ul else None

                for li in ul.xpath('./li'):
                    span_texts: tuple[str, str] = li.xpath('.//span/text()')
                    url["extra"].setdefault("language_stats", {})[span_texts[0]] = span_texts[1].rstrip("%")

        print(json.dumps(urls, indent=4))
        await browser.close()

asyncio.run(main())
