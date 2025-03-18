import asyncio
import aiohttp
import os
import json

from decrypt import decrypt

async def main():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.atptour.com/en/scores/stats-centre/archive/2024/421/qs010"
    }

    url = 'https://itp-atp-sls.infosys-platforms.com/static/prod/court-vision/2024/375/MS025/data.json'
    url = 'https://www.atptour.com/-/Hawkeye/MatchStats/Complete/2024/421/QS010'
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url) as resp:
            
            data_text = await resp.text()
            print(data_text)
            print(get_json_from_html(data_text))

url = 'https://www.atptour.com/-/Hawkeye/MatchStats/Complete/2024/421/QS010'


def selenium_test():
    import atptour

    atptour.driver.get(url)
    input()

def cloudscrapper_test():
    import cloudscraper

    scraper = cloudscraper.create_scraper()
    response = scraper.get(url)
    print(json.loads(response.text))


if __name__ == '__main__':
    # selenium_test()
    # asyncio.run(main())
    cloudscrapper_test()