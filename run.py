import asyncio
import aiohttp
import os
import json
from decrypt import decrypt
import cloudscraper
    


async def process_job(session: aiohttp.ClientSession, scraper: cloudscraper.CloudScraper, job: dict) -> None:
    """
    1. Fetch the encrypted JSON from job["url"].
    2. Decrypt it.
    3. Save to job["local_path"].
    4. Append parsed_type to match["parsed"].
    """
    url = job["url"]
    local_path = job["local_path"]
    parsed_type = job["parsed_type"]

    if job["match"]["parsed"]:
        return None

    # 1) HTTP GET
    if 'Hawkeye' not in url:
        async with session.get(url) as resp:
            try:
                resp.raise_for_status()  # If 4xx/5xx, raise an exception
            except Exception as e:
                print(e)
                return None
            try:
                data_json = await resp.json()  # Should conform to _Response structure
            except Exception as e:
                print(e)
                print('marked as error type')
                job["match"]["parsed"].append(e.__class__.__name__)
                return None
            # 2) Decrypt
            # data_json is like: { "lastModified": <int>, "response": <str> }

            payload = decrypt(data_json)
    else:
        response = scraper.get(url)
        payload = json.loads(response.text)


    # 3) Save to local path
    os.makedirs(os.path.dirname(local_path), exist_ok=True)  # Create dirs
    with open(local_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    # 4) Append to match["parsed"]
    job["match"]["parsed"].append(parsed_type)
    print(f"Saved {parsed_type} -> {local_path}")

# ---------------------------------------------------------------------
# Concurrency controller:
# ---------------------------------------------------------------------
async def run_jobs(jobs: list[dict], concurrency: int = 100) -> None:
    """
    Run download/decrypt jobs concurrently, up to `concurrency` at a time.
    """
    semaphore = asyncio.Semaphore(concurrency)

    cs = cloudscraper.create_scraper()
    async def sem_task(session, cs, j):
        async with semaphore:
            await process_job(session, cs, j)

    async with aiohttp.ClientSession() as session:
        tasks = [asyncio.create_task(sem_task(session, cs,job)) for job in jobs[::-1]]
        await asyncio.gather(*tasks, return_exceptions=False)


# ---------------------------------------------------------------------
# Example usage:
# ---------------------------------------------------------------------
if __name__ == "__main__":
    import asyncio

    # Example data:
    # example_data: Tournaments = {
    #     "tournaments": [
    #         {
    #             "name": "Test Open",
    #             "location": "Test City",
    #             "date": "2024-05-01",
    #             "year": 2024,
    #             "matches": [
    #                 {
    #                     "arena": "Center Court",
    #                     "duration": "2h 15m",
    #                     "link": "https://mysite.com/tournament/339/MS001",
    #                     "notes": "Quarter-Final",
    #                     "parsed": []
    #                 },
    #                 {
    #                     "arena": "Court 2",
    #                     "duration": "3h 00m",
    #                     "link": "https://mysite.com/tournament/339/MS002",
    #                     "notes": "Semi-Final",
    #                     "parsed": []
    #                 }
    #             ]
    #         }
    #     ]
    # }

    # 1) Build jobs
    with open('jobs.json') as f:
        download_jobs = json.load(f)

    # 2) Execute jobs asynchronously (100 at a time).
    #    If you have e.g. 500 jobs, it will keep 100 in-flight concurrently.
    try:
        asyncio.run(run_jobs(download_jobs, concurrency=50))
    except KeyboardInterrupt:
        print('KeyboardInterrupt')
    finally:
        with open('jobs.json', 'w') as f:
            json.dump(download_jobs, f, indent=4)
    # 3) Done! Each match in `example_data` will have "parsed" appended
    #    for each successful download/decrypt.
