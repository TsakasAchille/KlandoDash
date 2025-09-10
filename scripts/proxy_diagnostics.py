#!/usr/bin/env python3
"""
Comprehensive diagnostics for MapLibre resources via the local proxy.

It checks:
- style.json (status, content-type, encoding)
- vector tile samples for each source (z/x/y set)
- glyphs samples (0-255 range) if glyphs URL exists
- sprites (sprite.json, sprite.png) if sprite URL exists

Usage examples:
  python3 scripts/proxy_diagnostics.py \
      --host http://127.0.0.1:8050 \
      --style-url "https://geo.klando-carpool.com/styles/carpool/style.json" \
      --api-key <YOUR_KEY>

Notes:
- All requests go through /proxy/map?u=<percent-encoded-upstream>
- We read raw bytes to avoid client-side auto-decompression in requests
"""
import argparse
import json
import sys
from typing import Dict, Any, List, Tuple
from urllib.parse import urlparse, urlunparse, urlencode, parse_qsl, quote
import requests

DEFAULT_HOST = "http://127.0.0.1:8050"

SAMPLE_TILES: List[Tuple[int,int,int]] = [
    (5, 14, 14),
    (5, 15, 13),
    (6, 28, 28),
    (6, 29, 30),
    (7, 58, 59),
    (7, 59, 59),
]


def pct_encode(url: str) -> str:
    return quote(url, safe="")


def add_query_param(url: str, key: str, value: str) -> str:
    """Add or replace a query param to a URL (preserving others)."""
    parts = list(urlparse(url))
    q = dict(parse_qsl(parts[4], keep_blank_values=True))
    q[key] = value
    parts[4] = urlencode(q)
    return urlunparse(parts)


def via_proxy(host: str, upstream: str) -> str:
    return f"{host.rstrip('/')}/proxy/map?u={pct_encode(upstream)}"


def fetch_raw(url: str, timeout: float = 15.0):
    try:
        resp = requests.get(url, stream=True, timeout=timeout)
        # disable auto-decompression; read raw bytes
        try:
            if hasattr(resp, 'raw') and hasattr(resp.raw, 'decode_content'):
                resp.raw.decode_content = False
        except Exception:
            pass
        body = resp.raw.read()
        return resp, body
    except Exception as e:
        return e, None


def print_headers(prefix: str, resp: requests.Response):
    print(prefix)
    print("Status:", resp.status_code)
    print("Content-Type:", resp.headers.get("Content-Type"))
    print("Content-Encoding:", resp.headers.get("Content-Encoding"))
    print("Content-Length:", resp.headers.get("Content-Length"))
    xpe = resp.headers.get("X-Proxy-Error")
    if xpe:
        print("X-Proxy-Error:", xpe)


def hex_prefix(b: bytes, n: int = 16) -> str:
    if not b:
        return ""
    return " ".join(f"{x:02x}" for x in b[:n])


def main():
    ap = argparse.ArgumentParser(description="Diagnose style, tiles, glyphs, sprites via the proxy")
    ap.add_argument("--host", default=DEFAULT_HOST, help="Base URL of the Dash app (default: http://127.0.0.1:8050)")
    ap.add_argument("--style-url", required=True, help="Full style.json URL (without API key if passing --api-key)")
    ap.add_argument("--api-key", default="", help="API key to append if not already present in style-url")
    ap.add_argument("--tries", type=int, default=1, help="Number of tries per resource")
    args = ap.parse_args()

    style_url = args.style_url
    if args.api_key and "api_key=" not in style_url:
        style_url = add_query_param(style_url, "api_key", args.api_key)

    print("== STYLE ==")
    style_proxy = via_proxy(args.host, style_url)
    print("URL:", style_proxy)
    resp, body = fetch_raw(style_proxy)
    if isinstance(resp, Exception):
        print("ERROR fetching style:", repr(resp))
        sys.exit(1)
    print_headers("Style headers:", resp)
    print("Body size:", len(body))
    if not resp.headers.get("Content-Type", "").lower().startswith("application/json"):
        print("WARN: style response is not application/json")
    try:
        style = json.loads(body.decode("utf-8", errors="replace"))
    except Exception as e:
        print("ERROR: style JSON decode failed:", e)
        sys.exit(1)

    # Collect resources
    sprite = style.get("sprite")
    glyphs = style.get("glyphs")
    sources = style.get("sources", {})

    # Sprites
    if sprite:
        print("\n== SPRITES ==")
        # sprite URL can be a base; MapLibre appends .json and .png
        sprite_json = sprite if sprite.endswith(".json") else f"{sprite}.json"
        sprite_png = sprite if sprite.endswith(".png") else f"{sprite}.png"
        for label, url in [("sprite.json", sprite_json), ("sprite.png", sprite_png)]:
            u = url
            if args.api_key and "api_key=" not in u:
                u = add_query_param(u, "api_key", args.api_key)
            p = via_proxy(args.host, u)
            print(f"Testing {label}: {p}")
            r, b = fetch_raw(p)
            if isinstance(r, Exception):
                print(f"ERROR fetching {label}:", repr(r))
                continue
            print_headers(f"{label} headers:", r)
            print(f"{label} size:", len(b))
            if label.endswith('.json') and not (r.headers.get('Content-Type','').lower().startswith('application/json')):
                print("WARN: sprite.json Content-Type not application/json")
            if label.endswith('.png') and not (r.headers.get('Content-Type','').lower().startswith('image/')):
                print("WARN: sprite.png Content-Type not image/*")

    # Glyphs
    if glyphs:
        print("\n== GLYPHS ==")
        # Replace {fontstack}/{range}.pbf
        sample_stack = "Noto Sans Regular"  # common in your config
        sample_range = "0-255"
        g_url = glyphs.replace("{fontstack}", sample_stack).replace("{range}", sample_range)
        if args.api_key and "api_key=" not in g_url:
            g_url = add_query_param(g_url, "api_key", args.api_key)
        p = via_proxy(args.host, g_url)
        print("Testing glyphs:", p)
        r, b = fetch_raw(p)
        if isinstance(r, Exception):
            print("ERROR fetching glyphs:", repr(r))
        else:
            print_headers("glyphs headers:", r)
            print("glyphs size:", len(b))
            if not (r.headers.get('Content-Type','').lower().startswith('application/x-protobuf')):
                print("WARN: glyphs Content-Type not application/x-protobuf")

    # Sources and tiles
    print("\n== SOURCES & TILES ==")
    for sid, src in sources.items():
        st = src.get("type")
        tiles = src.get("tiles") or []
        url = src.get("url")
        print(f"[SOURCE] id={sid} type={st} tiles={len(tiles)} url={url}")
        if tiles:
            # Pick first tile template, sample a few z/x/y
            ttpl = tiles[0]
            for (z, x, y) in SAMPLE_TILES:
                tpl = ttpl.replace("{z}", str(z)).replace("{x}", str(x)).replace("{y}", str(y))
                u = tpl
                if args.api_key and "api_key=" not in u:
                    u = add_query_param(u, "api_key", args.api_key)
                p = via_proxy(args.host, u)
                print(f"Tile {z}/{x}/{y}: {p}")
                r, b = fetch_raw(p)
                if isinstance(r, Exception):
                    print("ERROR:", repr(r))
                    continue
                print_headers("tile headers:", r)
                print("tile size:", len(b))
                print("tile hex prefix:", hex_prefix(b))
                if not (r.headers.get('Content-Type','').lower().startswith('application/x-protobuf')):
                    print("WARN: tile Content-Type not application/x-protobuf")

    print("\nDone.")


if __name__ == "__main__":
    main()
