import base64
import random

BASE64_STANDARD_ALPHABET = (
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
)
BASE64_SWMS_ALPHABET = (
    "fghijklmnopqrstuvwxyz6789012345ABCDEFGHIJKLMNOPQRSTUZabcdeVWXY+/"
)
BASE64_SWMS_ENCODE_TRANS = str.maketrans(BASE64_STANDARD_ALPHABET, BASE64_SWMS_ALPHABET)
BASE64_SWMS_DECODE_TRANS = str.maketrans(BASE64_SWMS_ALPHABET, BASE64_STANDARD_ALPHABET)


def swms_base64_encode(input: str) -> str:
    if input.startswith("swms121"):
        return input
    return (
        "swms121"
        + base64.b64encode(input.encode())
        .decode()
        .translate(BASE64_SWMS_ENCODE_TRANS)
        .replace("=", "sdhs")
        + str(random.randint(1, 2))
    )


def swms_base64_decode(input: str) -> str:
    if not input.startswith("swms121"):
        return input
    return base64.b64decode(
        input[7:-1].replace("sdhs", "=").translate(BASE64_SWMS_DECODE_TRANS)
    ).decode()
