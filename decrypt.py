from typing import Final, TypedDict
import json
import base64

# Reuse your existing AES logic here:
from Crypto.Cipher import AES

class _Response(TypedDict):
    lastModified: int
    response: str

def _remove_padding(data: bytes) -> bytes:
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

def decrypt(data_json: _Response) -> dict:
    last_modified = data_json["lastModified"]
    encrypted_b64 = data_json["response"]

    key, iv = _get_key_and_iv(last_modified)

    encrypted_payload = base64.b64decode(encrypted_b64)
    decrypted_bytes = _decrypt(key, iv, encrypted_payload)
    # Remove PKCS#7 or custom padding:
    decrypted_bytes = _remove_padding(decrypted_bytes)

    return json.loads(decrypted_bytes)
