#!/usr/bin/env python3
import argparse
import sys
import json
from urllib.parse import urlencode, quote, unquote, urlparse, parse_qs, urlunparse, parse_qsl

import requests


def fetch(url: str) -> requests.Response:
    try:
        resp = requests.get(url, timeout=20)
        return resp
    except requests.RequestException as e:
        print(f"[ERROR] Request failed: {e}")
        sys.exit(2)


def print_resp(label: str, resp: requests.Response):
    ct = resp.headers.get('Content-Type', '')
    print(f"\n=== {label} ===")
    print(f"Status: {resp.status_code}")
    print(f"Content-Type: {ct}")
    # print small preview
    try:
        text = resp.text
        preview = text[:200].replace('\n', ' ')
        print(f"Body preview: {preview}{'...' if len(text) > 200 else ''}")
    except Exception:
        print("Body: <non-text>")


def set_api_key(url: str, api_key: str) -> str:
    """Return URL with api_key added if missing (does not duplicate)."""
    try:
        if not api_key:
            return url
        parts = urlparse(url)
        qs = dict(parse_qsl(parts.query, keep_blank_values=True))
        if 'api_key' not in qs and 'key' not in qs:
            qs['api_key'] = api_key
        return urlunparse(parts._replace(query=urlencode(qs)))
    except Exception:
        return url


def proxy_inner(url: str, proxy_base: str) -> str:
    return f"{proxy_base}?u={quote(url, safe='')}"


def proxy_outer_with_key(url: str, proxy_base: str, api_key: str) -> str:
    # WRONG way on purpose: add the key to the OUTER proxy URL, not inner 'u'
    base = proxy_inner(url, proxy_base)
    joiner = '&' if '?' in base else '?'
    return f"{base}{joiner}api_key={api_key}"


def main():
    ap = argparse.ArgumentParser(description="Test direct vs proxied fetch of a MapLibre style URL and its sub-resources")
    ap.add_argument("--url", required=True, help="Target style URL (with or without api_key)")
    ap.add_argument("--proxy", default="http://127.0.0.1:8050/proxy/map", help="Local proxy endpoint")
    ap.add_argument("--api-key", default="", help="API key to add when missing for tests")
    args = ap.parse_args()

    target = args.url
    proxy = args.proxy.rstrip('/')
    api_key = args.api_key

    print(f"Target: {target}")
    print(f"Proxy:  {proxy}")

    # Normalize a version WITH key
    target_with_key = set_api_key(target, api_key)
    target_no_key = target

    # Direct (no key / with key)
    resp_direct_nokey = fetch(target_no_key)
    print_resp("Direct (no key)", resp_direct_nokey)
    resp_direct_withkey = fetch(target_with_key)
    print_resp("Direct (with key)", resp_direct_withkey)

    # If JSON, try to parse and list sprite/glyph/tiles hosts (lightweight)
    try:
        data = resp_direct_withkey.json() if resp_direct_withkey.ok else resp_direct_nokey.json()
        print("\n--- Parsed style.json keys ---")
        for k in ("sprite", "glyphs"):
            v = data.get(k)
            if v:
                print(f"{k}: {v}")
        sources = data.get("sources", {})
        if sources:
            print(f"sources: {list(sources.keys())}")
    except Exception:
        pass

    # Proxied tests
    prox_inner_nokey = proxy_inner(target_no_key, proxy)
    prox_inner_withkey = proxy_inner(target_with_key, proxy)
    prox_outer_withkey_wrong = proxy_outer_with_key(target_no_key, proxy, api_key) if api_key else None

    print(f"\nProxied (inner no key): {prox_inner_nokey}")
    print_resp("Proxied (inner no key)", fetch(prox_inner_nokey))

    print(f"\nProxied (inner with key): {prox_inner_withkey}")
    resp_proxy_inner = fetch(prox_inner_withkey)
    print_resp("Proxied (inner with key)", resp_proxy_inner)

    if prox_outer_withkey_wrong:
        print(f"\nProxied (WRONG: outer key): {prox_outer_withkey_wrong}")
        print_resp("Proxied (WRONG: outer key)", fetch(prox_outer_withkey_wrong))

    # Derive a glyph and a tile URL when possible and test them as well
    try:
        style = resp_proxy_inner.json() if resp_proxy_inner.ok else {}
        glyphs_tpl = style.get('glyphs')
        test_urls = []
        if glyphs_tpl:
            # pick a common fontstack and range
            glyph_url = glyphs_tpl.replace('{fontstack}', 'Open Sans Regular,Arial Unicode MS Regular').replace('{range}', '0-255')
            test_urls.append(('Glyph', glyph_url))
        srcs = style.get('sources', {})
        for name, src in srcs.items():
            tiles = src.get('tiles') if isinstance(src, dict) else None
            if tiles and isinstance(tiles, list) and tiles:
                test_urls.append((f"Tile({name})", tiles[0]))
                break
        if test_urls:
            print("\n--- Sub-resource tests ---")
            for label, base_url in test_urls:
                direct_wk = set_api_key(base_url, api_key)
                print(f"Direct {label} (with key): {direct_wk}")
                print_resp(f"Direct {label} (with key)", fetch(direct_wk))

                prox_inner = proxy_inner(direct_wk, proxy)
                print(f"Proxied {label} (inner with key): {prox_inner}")
                print_resp(f"Proxied {label} (inner with key)", fetch(prox_inner))
    except Exception:
        pass

    # Exit code: success if proxied inner-with-key of style is 200
    ok = resp_proxy_inner.ok
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
