import asyncio
import aiohttp
import os
import json
import base64
from typing import Final, Dict, Any

# Reuse your existing AES logic here:
from Crypto.Cipher import AES

# ---------------------------------------------------------------------
# Decryption helpers from your snippet:
# ---------------------------------------------------------------------
def remove_padding(data: bytes) -> bytes:
    # Get the value of the last byte
    padding_len = data[-1]
    # Validate and remove the padding
    if padding_len > 0 and all(byte == padding_len for byte in data[-padding_len:]):
        return data[:-padding_len]
    raise ValueError("Invalid padding in decrypted payload")

def _integer_to_string_with_radix(value: int, radix: int) -> str:
    import string
    from io import StringIO
    if value < 0:
        raise ValueError("Negative unsupported.")
    alphabet = string.digits + string.ascii_letters
    if radix < 2 or radix > len(alphabet):
        raise ValueError(f"Supported radix range is 2-{len(alphabet)}.")
    with StringIO() as buffer:
        while value > 0:
            buffer.write(alphabet[value % radix])
            value //= radix
        return buffer.getvalue()[::-1]

def _get_key_and_iv(last_modified_timestamp: int) -> tuple[bytes, bytes]:
    from datetime import datetime, timezone
    # Convert to radix 16
    tmp: int = int(str(last_modified_timestamp), base=16)
    # Reinterpret as radix 36
    key_str: str = _integer_to_string_with_radix(tmp, 36)

    # Python works with seconds in float, preserve milliseconds
    last_modified_date = datetime.fromtimestamp(last_modified_timestamp / 1000, tz=timezone.utc)
    current_day_reversed = int(f"{last_modified_date.day:02d}"[::-1])
    current_year_reversed = int(str(last_modified_date.year)[::-1])
    tmp = (last_modified_date.day + current_day_reversed) * (last_modified_date.year + current_year_reversed)
    key_str += _integer_to_string_with_radix(tmp, 24)

    # Crop to 14 characters and pad with zeros if less
    key_encoded = f"#{key_str[:14]:014s}$".encode()
    return key_encoded, key_encoded.upper()

def _decrypt(key: bytes, iv: bytes, data: bytes) -> bytes:
    return AES.new(key, AES.MODE_CBC, iv=iv).decrypt(data)

# ---------------------------------------------------------------------
# Async job processing:
# ---------------------------------------------------------------------
async def process_job(session: aiohttp.ClientSession, job: Dict[str, Any]) -> None:
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

    if 'Hawkeye' not in url:
        last_modified = data_json["lastModified"]
        encrypted_b64 = data_json["response"]

        key, iv = _get_key_and_iv(last_modified)

        encrypted_payload = base64.b64decode(encrypted_b64)
        decrypted_bytes = _decrypt(key, iv, encrypted_payload)
        # Remove PKCS#7 or custom padding:
        decrypted_bytes = remove_padding(decrypted_bytes)

        payload = json.loads(decrypted_bytes)
    else:
        payload = data_json

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
async def run_jobs(jobs: list[Dict[str, Any]], concurrency: int = 100) -> None:
    """
    Run download/decrypt jobs concurrently, up to `concurrency` at a time.
    """
    semaphore = asyncio.Semaphore(concurrency)

    async def sem_task(session, j):
        async with semaphore:
            await process_job(session, j)

    async with aiohttp.ClientSession() as session:
        tasks = [asyncio.create_task(sem_task(session, job)) for job in jobs[::-1]]
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
