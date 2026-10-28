from app.services import search_service


def test_serper_uses_dynamic_query_and_actual_api_key(monkeypatch):
    monkeypatch.setenv("SERPER_API_KEY", "test-serper-key")
    calls = {}

    class Response:
        def raise_for_status(self):
            pass

        def json(self):
            return {"organic": [{
                "title": "Demo Person - LinkedIn",
                "snippet": "Learning AI",
                "link": "https://www.linkedin.com/in/demo-person/",
            }]}

    def fake_post(url, **kwargs):
        calls["url"] = url
        calls.update(kwargs)
        return Response()

    monkeypatch.setattr(search_service.requests, "post", fake_post)

    profiles, source = search_service.search_profiles("Fresher", "AI engineer", use_mock=False)

    assert source == "serper"
    assert calls["url"] == "https://google.serper.dev/search"
    assert calls["headers"]["X-API-KEY"] == "test-serper-key"
    assert calls["json"]["q"] == 'site:linkedin.com/in/ "AI engineer"'
    assert profiles[0].url == "https://www.linkedin.com/in/demo-person/"


def test_missing_serper_key_falls_back_to_mock(monkeypatch):
    monkeypatch.delenv("SERPER_API_KEY", raising=False)

    profiles, source = search_service.search_profiles("Fresher", use_mock=False)

    assert profiles
    assert source == "mock (Serper API key missing)"


def test_serper_timeout_falls_back_to_mock_without_exposing_error(monkeypatch):
    monkeypatch.setenv("SERPER_API_KEY", "test-serper-key")

    def raise_timeout(*args, **kwargs):
        raise search_service.requests.Timeout("request failed")

    monkeypatch.setattr(search_service.requests, "post", raise_timeout)

    profiles, source = search_service.search_profiles("Fresher", use_mock=False)

    assert profiles
    assert source == "mock (Serper unavailable)"


def test_invalid_serper_response_falls_back_to_mock(monkeypatch):
    monkeypatch.setenv("SERPER_API_KEY", "test-serper-key")

    class Response:
        def raise_for_status(self):
            pass

        def json(self):
            return {"organic": "invalid"}

    monkeypatch.setattr(search_service.requests, "post", lambda *args, **kwargs: Response())

    profiles, source = search_service.search_profiles("Fresher", use_mock=False)

    assert profiles
    assert source == "mock (Serper unavailable)"