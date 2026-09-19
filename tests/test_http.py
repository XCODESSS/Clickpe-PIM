
from clickpe_pim.collect.http import HttpCollector
from clickpe_pim.collect.policy import check_policy


class FakeResponse:
    def __init__(self, status_code, body=b"", headers=None):
        self.status_code = status_code
        self.body = body
        self.headers = headers or {}

    def iter_content(self, size):
        yield self.body

    def close(self):
        return None


class FakeSession:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def get(self, *args, **kwargs):
        self.calls.append((args, kwargs))
        item = self.responses.pop(0)
        if isinstance(item, Exception):
            raise item
        return item


def test_robots_disallow_is_honoured():
    assert not check_policy("https://example.org/private/x", "ClickPePIM", "User-agent: *\nDisallow: /private/", 200)


def test_unknown_robots_health_is_not_permission():
    assert not check_policy("https://example.org/", "ClickPePIM", "", 503)


def test_retry_then_success(settings):
    sleeps = []
    collector = HttpCollector(settings, FakeSession([FakeResponse(503), FakeResponse(200, b"ok", {"Content-Type": "text/html"})]), sleeps.append)
    result = collector.fetch("https://example.org/x", allowed_hosts={"example.org"})
    assert result.status == "ok" and result.body == b"ok"
    assert 2 in sleeps


def test_captcha_and_redirect_are_blocked(settings):
    captcha = HttpCollector(settings, FakeSession([FakeResponse(200, b"Please verify you are human")]), lambda _: None)
    assert captcha.fetch("https://example.org", allowed_hosts={"example.org"}).status == "blocked"
    redirect = HttpCollector(settings, FakeSession([FakeResponse(302, headers={"Location": "https://evil.example/x"})]), lambda _: None)
    assert redirect.fetch("https://example.org", allowed_hosts={"example.org"}).error_code == "redirect_not_allowed"

