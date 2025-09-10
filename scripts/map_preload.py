#!/usr/bin/env python3
"""
Preload MapLibre resources through the local proxy to warm caches before opening the app.

What it does:
- Fetches style.json via /proxy/map
- Fetches sprite.json and sprite.png if defined
- Fetches a glyphs sample (for a common fontstack and ranges)
- Computes tiles covering a given viewport (center + zoom + radius in tiles) and preloads them for a set of zoom levels
- Optionally opens the app in your default browser after preloading

Usage examples:
  python3 scripts/map_preload.py \
    --host http://127.0.0.1:8050 \
    --style-url "https://geo.klando-carpool.com/styles/carpool/style.json" \
    --api-key <YOUR_KEY> \
    --center 45.76 4.84 \
    --zooms 5 6 7 8 \
    --radius 2 \
    --open-browser

Notes:
- All requests go through /proxy/map?u=<percent-encoded-upstream>
- This script just warms caches; browser cache is per-device. It will still help initial loads.
"""
import argparse
import json
import sys
import time
import webbrowser
from math import log, tan, radians, cos, pi
from typing import List, Tuple
from urllib.parse import urlparse, urlunparse, urlencode, parse_qsl, quote

import requests

DEFAULT_HOST = "http://127.0.0.1:8050"
DEFAULT_CENTER = (45.76, 4.84)  # Lyon as default
DEFAULT_ZOOMS = [5, 6, 7]
DEFAULT_RADIUS = 2  # tiles around center tile per zoom


def pct_encode(url: str) -> str:
    return quote(url, safe="")


def add_query_param(url: str, key: str, value: str) -> str:
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
        try:
            if hasattr(resp, 'raw') and hasattr(resp.raw, 'decode_content'):
                resp.raw.decode_content = False
        except Exception:
            pass
        body = resp.raw.read()
        return resp, body
    except Exception as e:
        return e, None


def print_line(label: str, url: str, resp: requests.Response, size: int):
    ct = resp.headers.get('Content-Type')
    ce = resp.headers.get('Content-Encoding')
    cl = resp.headers.get('Content-Length')
    print(f"- {label}: {url}\n  -> {resp.status_code} {ct} enc={ce} len={cl or size}")


def lonlat_to_tile(lon: float, lat: float, z: int) -> Tuple[int, int]:
    # Web mercator tile math
    lat = max(min(lat, 85.05112878), -85.05112878)
    n = 2 ** z
    xtile = int((lon + 180.0) / 360.0 * n)
    ytile = int((1.0 - log(tan(radians(lat)) + 1 / cos(radians(lat))) / pi) / 2.0 * n)
    return xtile, ytile


def build_tile_urls(tiles_template: str, z: int, x_center: int, y_center: int, radius: int, api_key: str) -> List[str]:
    urls = []
    for dx in range(-radius, radius + 1):
        for dy in range(-radius, radius + 1):
            x = x_center + dx
            y = y_center + dy
            u = tiles_template.replace('{z}', str(z)).replace('{x}', str(x)).replace('{y}', str(y))
            if api_key and 'api_key=' not in u:
                u = add_query_param(u, 'api_key', api_key)
            urls.append(u)
    return urls


def main():
    ap = argparse.ArgumentParser(description="Preload MapLibre resources via the local proxy")
    ap.add_argument('--host', default=DEFAULT_HOST)
    ap.add_argument('--style-url', required=True)
    ap.add_argument('--api-key', default='')
    ap.add_argument('--center', nargs=2, type=float, default=DEFAULT_CENTER, metavar=('LAT', 'LON'))
    ap.add_argument('--zooms', nargs='+', type=int, default=DEFAULT_ZOOMS)
    ap.add_argument('--radius', type=int, default=DEFAULT_RADIUS)
    ap.add_argument('--open-browser', action='store_true')
    args = ap.parse_args()

    style_url = args.style_url
    if args.api_key and 'api_key=' not in style_url:
        style_url = add_query_param(style_url, 'api_key', args.api_key)

    # 1) Style
    style_proxy = via_proxy(args.host, style_url)
    r, b = fetch_raw(style_proxy)
    if isinstance(r, Exception):
        print('ERROR fetching style:', repr(r))
        sys.exit(1)
    print_line('style.json', style_proxy, r, len(b))

    try:
        style = json.loads(b.decode('utf-8', errors='replace'))
    except Exception as e:
        print('ERROR: style JSON decode failed:', e)
        sys.exit(1)

    # 2) Sprites
    sprite = style.get('sprite')
    if sprite:
        sprite_json = sprite if sprite.endswith('.json') else f"{sprite}.json"
        sprite_png = sprite if sprite.endswith('.png') else f"{sprite}.png"
        for label, url in [("sprite.json", sprite_json), ("sprite.png", sprite_png)]:
            u = url
            if args.api_key and 'api_key=' not in u:
                u = add_query_param(u, 'api_key', args.api_key)
            p = via_proxy(args.host, u)
            rr, bb = fetch_raw(p)
            if isinstance(rr, Exception):
                print(f"ERROR fetching {label}:", repr(rr))
            else:
                print_line(label, p, rr, len(bb))

    # 3) Glyphs sample
    glyphs = style.get('glyphs')
    if glyphs:
        sample_stack = 'Noto Sans Regular'
        sample_range = '0-255'
        g_url = glyphs.replace('{fontstack}', sample_stack).replace('{range}', sample_range)
        if args.api_key and 'api_key=' not in g_url:
            g_url = add_query_param(g_url, 'api_key', args.api_key)
        p = via_proxy(args.host, g_url)
        rr, bb = fetch_raw(p)
        if isinstance(rr, Exception):
            print('ERROR fetching glyphs:', repr(rr))
        else:
            print_line('glyphs.pbf', p, rr, len(bb))

    # 4) Tiles for selected sources
    sources = style.get('sources', {})
    lat, lon = args.center
    for sid, src in sources.items():
        tiles = src.get('tiles') or []
        if not tiles:
            continue
        tpl = tiles[0]
        print(f"[SOURCE] {sid} -> {tpl}")
        for z in args.zooms:
            x, y = lonlat_to_tile(lon, lat, z)
            urls = build_tile_urls(tpl, z, x, y, args.radius, args.api_key)
            print(f"  Zoom {z}: preloading {len(urls)} tiles around x={x}, y={y}")
            for u in urls:
                p = via_proxy(args.host, u)
                rr, bb = fetch_raw(p)
                if isinstance(rr, Exception):
                    print('  ERROR:', repr(rr))
                else:
                    print_line(f'tile z{z}', p, rr, len(bb))
                time.sleep(0.05)

    # Optionally open the app
    if args.open_browser:
        app_url = args.host
        print('Opening app:', app_url)
        try:
            webbrowser.open(app_url)
        except Exception:
            pass


if __name__ == '__main__':
    main()
