#!/usr/bin/env python3
import argparse
import sys
import time
from urllib.parse import quote
import requests

DEFAULT_HOST = "http://127.0.0.1:8050"

TEST_TILES = [
    (5, 14, 14),
    (5, 15, 13),
    (6, 28, 28),
    (6, 29, 30),
    (7, 58, 59),
    (7, 59, 59),
]


def build_proxy_url(host: str, upstream_url: str) -> str:
    enc = quote(upstream_url, safe="")
    return f"{host.rstrip('/')}/proxy/map?u={enc}"


def fetch(url: str, timeout: float = 12.0):
    try:
        # Ask proxy to avoid compression for easier diagnostics
        resp = requests.get(url, stream=True, timeout=timeout, headers={
            'Accept-Encoding': 'identity'
        })
        try:
            # Ensure urllib3 does not auto-decompress; we want raw bytes
            if hasattr(resp, 'raw') and hasattr(resp.raw, 'decode_content'):
                resp.raw.decode_content = False
        except Exception:
            pass
        body = resp.content  # buffer into memory for inspection
        return resp, body
    except Exception as e:
        return e, None


def hex_prefix(b: bytes, n: int = 16) -> str:
    if not b:
        return ""
    return " ".join(f"{x:02x}" for x in b[:n])


def main():
    ap = argparse.ArgumentParser(description="Test MapLibre proxy tile fetching and headers")
    ap.add_argument("--host", default=DEFAULT_HOST, help="Base URL of the Dash app (default: http://127.0.0.1:8050)")
    ap.add_argument("--api-key", required=True, help="API key to append to upstream tile URLs")
    ap.add_argument("--style-base", default="https://geo.klando-carpool.com/data/klando-carpool-map-sn-v1.1", help="Base path for tiles upstream")
    ap.add_argument("--tries", type=int, default=1, help="Number of tries per tile")
    args = ap.parse_args()

    print(f"Host: {args.host}")
    print(f"Style base: {args.style_base}")

    for (z, x, y) in TEST_TILES:
        upstream = f"{args.style_base}/{z}/{x}/{y}.pbf?api_key={args.api_key}"
        proxy_url = build_proxy_url(args.host, upstream)
        for t in range(args.tries):
            print("\n=== TILE z/x/y:", z, x, y, f"(try {t+1}/{args.tries}) ===")
            print("Upstream:", upstream)
            print("Proxy URL:", proxy_url)
            resp, body = fetch(proxy_url)
            if isinstance(resp, Exception):
                print("ERROR:", repr(resp))
                continue
            print("Status:", resp.status_code)
            print("Content-Type:", resp.headers.get("Content-Type"))
            print("Content-Encoding:", resp.headers.get("Content-Encoding"))
            print("Content-Length:", resp.headers.get("Content-Length"))
            print("Body size:", len(body) if body is not None else 0)
            print("Body hex prefix:", hex_prefix(body, 16))
            # crude protobuf sanity: non-empty and not starting with '<!DO' or '{<'
            if body and body[:4] in (b"<!DO", b"<htm", b"{\"ht"):
                print("WARN: Body looks like HTML/JSON, not protobuf")
            time.sleep(0.2)


if __name__ == "__main__":
    main()
