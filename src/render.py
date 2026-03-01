import zlib
import base64


def plantuml_encode(text):
    zlibbed = zlib.compress(text.encode("utf-8"))
    compressed = zlibbed[2:-4]
    return encode_base64(compressed)


def encode_base64(data):
    alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_"
    res = ""

    for i in range(0, len(data), 3):
        b1 = data[i]
        b2 = data[i + 1] if i + 1 < len(data) else 0
        b3 = data[i + 2] if i + 2 < len(data) else 0

        c1 = b1 >> 2
        c2 = ((b1 & 0x3) << 4) | (b2 >> 4)
        c3 = ((b2 & 0xF) << 2) | (b3 >> 6)
        c4 = b3 & 0x3F

        res += alphabet[c1] + alphabet[c2] + alphabet[c3] + alphabet[c4]

    return res


def plantuml_url(plantuml_text):
    encoded = plantuml_encode(plantuml_text)
    return f"https://www.plantuml.com/plantuml/png/{encoded}"