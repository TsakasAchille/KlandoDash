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

    if parsed.hostname not in ALLOWED_HOSTS:
        abort(403, 'Upstream host not allowed')

    # Append API key if configured
    upstream_url = _append_api_key(upstream_url, Config.MAPLIBRE_API_KEY)

    try:
        resp = requests.get(upstream_url, stream=True, timeout=20)
    except requests.RequestException as e:
        logger.exception("Proxy fetch error: %s", e)
        abort(502, 'Upstream fetch failed')

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

    return Response(resp.content, status=resp.status_code, headers=headers)
