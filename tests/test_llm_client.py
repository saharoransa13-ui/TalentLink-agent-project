"""Tests for retrying LLM requests when the server is busy."""

from backend import llm_client


class FakeResponse:
    def __init__(self, status_code, headers=None):
        self.status_code = status_code
        self.headers = headers or {}


def _fake_post_returning(statuses, calls):
    def fake_post(url, **kwargs):
        calls.append(url)
        return FakeResponse(statuses[len(calls) - 1])
    return fake_post


def test_retries_after_rate_limit_then_succeeds(monkeypatch):
    calls, waits = [], []
    monkeypatch.setattr(llm_client.requests, "post", _fake_post_returning([429, 200], calls))
    response = llm_client.post_with_retry("https://llm.test", sleep=waits.append)
    assert response.status_code == 200
    assert len(calls) == 2
    assert waits == [2.0]


def test_stops_after_max_retries(monkeypatch):
    calls, waits = [], []
    monkeypatch.setattr(llm_client.requests, "post", _fake_post_returning([429, 429, 429], calls))
    response = llm_client.post_with_retry("https://llm.test", sleep=waits.append)
    assert response.status_code == 429
    assert len(calls) == llm_client.MAX_RETRIES + 1


def test_does_not_retry_client_errors(monkeypatch):
    calls, waits = [], []
    monkeypatch.setattr(llm_client.requests, "post", _fake_post_returning([401], calls))
    response = llm_client.post_with_retry("https://llm.test", sleep=waits.append)
    assert response.status_code == 401
    assert len(calls) == 1
    assert waits == []


def test_uses_retry_after_header_with_a_cap():
    assert llm_client._wait_seconds(FakeResponse(429, {"Retry-After": "3"}), 0) == 3.0
    assert llm_client._wait_seconds(FakeResponse(429, {"Retry-After": "60"}), 0) == 10.0
