import base64
import hashlib


def get_hash_sha256(*, data: str, use_base64: bool = True) -> str:
    h = hashlib.sha256(string=data.encode("utf-8")).digest()
    if use_base64:
        return base64.urlsafe_b64encode(s=h).decode("utf-8")
    return h.hex()