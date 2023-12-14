import base64


def encodeStringToBase64(text):
    text_bytes = text.encode("ascii")
    base64_bytes = base64.b64encode(text_bytes)
    return base64_bytes.decode("ascii")
