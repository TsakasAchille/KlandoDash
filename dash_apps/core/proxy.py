import os
import logging
from typing import Optional
from urllib.parse import urlparse, urlencode, urlunparse, parse_qsl

import requests
from flask import Blueprint, request, Response, abort

from dash_apps.config import Config

logger = logging.getLogger(__name__)

proxy_bp = Blueprint('proxy', __name__)

# Allow-list of upstream hosts we proxy to
ALLOWED_HOSTS = {
    'geo.klando-carpool.com',
    'demotiles.maplibre.org',
}


def _append_api_key(url: str, api_key: Optional[str]) -> str:
    if not api_key:
        return url
    try:
        parts = urlparse(url)
        qs = dict(parse_qsl(parts.query, keep_blank_values=True))
        if 'api_key' not in qs and 'key' not in qs:
            qs['api_key'] = api_key
        new_query = urlencode(qs)
        return urlunparse(parts._replace(query=new_query))
    except Exception:
        return url


@proxy_bp.route('/map')
def proxy_map():
    """
    Proxy endpoint to bypass CORS for MapLibre resources.
    Usage: /proxy/map?u=<encoded_upstream_url>
    Appends api_key when needed and forwards method/headers minimally.
    """
    upstream_url = request.args.get('u')
    if not upstream_url:
        abort(400, 'Missing parameter u')

    try:
        parsed = urlparse(upstream_url)
    except Exception:
        abort(400, 'Invalid URL')

    if parsed.scheme not in ('http', 'https'):
        abort(400, 'Unsupported URL scheme')

    if parsed.hostname not in ALLOWED_HOSTS:
        abort(403, 'Upstream host not allowed')

    # Append API key if configured
    upstream_url = _append_api_key(upstream_url, Config.MAPLIBRE_API_KEY)

    try:
        # Forward minimal headers that matter for range requests and content negotiation
        fwd_headers = {}
        if 'Range' in request.headers:
            fwd_headers['Range'] = request.headers['Range']
        if 'If-None-Match' in request.headers:
            fwd_headers['If-None-Match'] = request.headers['If-None-Match']
        if 'If-Modified-Since' in request.headers:
            fwd_headers['If-Modified-Since'] = request.headers['If-Modified-Since']

        resp = requests.get(upstream_url, stream=True, timeout=5, headers=fwd_headers)
    except requests.RequestException as e:
        logger.warning("Proxy fetch error: %s", e)
        # Return empty response instead of aborting to avoid blocking the UI
        return Response('', status=204, headers={'Access-Control-Allow-Origin': '*'})

    # Build Flask response
    excluded_headers = {'content-encoding', 'transfer-encoding', 'connection'}
    headers = [(name, value) for name, value in resp.headers.items() if name.lower() not in excluded_headers]
    # Ensure CORS for our app
    headers.append(('Access-Control-Allow-Origin', '*'))
    headers.append(('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept, Range'))

    # Ensure content-type is preserved
    content_type = resp.headers.get('Content-Type')
    if content_type:
        headers = [(k, v) for (k, v) in headers if k.lower() != 'content-type']
        headers.append(('Content-Type', content_type))

    # Add light caching when upstream didn't provide any, beneficial for tiles/glyphs
    cache_hdr_present = any(k.lower() == 'cache-control' for k, _ in headers)
    if not cache_hdr_present and content_type:
        if any(substr in content_type for substr in ('protobuf', 'pbf', 'mvt', 'font', 'octet-stream', 'application/json')):
            headers.append(('Cache-Control', 'public, max-age=3600'))

    # Stream body to client without buffering everything in memory
    return Response(resp.iter_content(chunk_size=8192), status=resp.status_code, headers=headers)
