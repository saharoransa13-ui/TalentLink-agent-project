"""Small helper that sends a request to the LLM and retries when the server is busy."""

import time

import requests

# 429 = too many requests (rate limit). 5xx = temporary server problem.
RETRY_STATUS_CODES = {429, 500, 502, 503, 504}
MAX_RETRIES = 2
MAX_WAIT_SECONDS = 10.0


def _wait_seconds(response, attempt: int) -> float:
    """Use the server's Retry-After header when it gives one, otherwise wait 2s, then 4s."""
    retry_after = response.headers.get("Retry-After") if response is not None else None
    try:
        seconds = float(retry_after)
    except (TypeError, ValueError):
        seconds = 2.0 * (2 ** attempt)
    return min(max(seconds, 0.0), MAX_WAIT_SECONDS)


def post_with_retry(url: str, *, sleep=time.sleep, **kwargs):
    """Same as requests.post, but tries again when the LLM server is busy."""
    for attempt in range(MAX_RETRIES + 1):
        response = requests.post(url, **kwargs)
        status = getattr(response, "status_code", 200)
        if status not in RETRY_STATUS_CODES or attempt == MAX_RETRIES:
            return response
        sleep(_wait_seconds(response, attempt))
    return response
