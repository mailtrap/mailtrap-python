import os
from wsgiref.simple_server import make_server

import mailtrap as mt

SIGNING_SECRET = os.environ["MAILTRAP_WEBHOOK_SIGNING_SECRET"]


def app(environ, start_response):
    # Use the raw request body — parsing and re-serializing the JSON may
    # reorder keys or alter whitespace and invalidate the signature.
    length = int(environ.get("CONTENT_LENGTH") or 0)
    payload = environ["wsgi.input"].read(length).decode("utf-8")
    signature = environ.get("HTTP_MAILTRAP_SIGNATURE", "")

    if not mt.verify_signature(payload, signature, SIGNING_SECRET):
        start_response("401 Unauthorized", [("Content-Type", "text/plain")])
        return [b"Invalid signature"]

    start_response("200 OK", [("Content-Type", "text/plain")])
    return [b""]


if __name__ == "__main__":
    with make_server("", 9292, app) as server:
        server.serve_forever()
