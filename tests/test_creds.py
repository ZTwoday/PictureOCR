import security.creds as creds


def test_save_get_roundtrip(monkeypatch):
    monkeypatch.setattr(creds, "TARGET", "ocr_app_test_creds")
    try:
        creds.save_baidu_creds("ak-123", "sk-456")
        assert creds.get_baidu_creds() == ("ak-123", "sk-456")
    finally:
        creds.delete_baidu_creds()


def test_get_returns_none_when_missing(monkeypatch):
    monkeypatch.setattr(creds, "TARGET", "ocr_app_missing_creds")
    creds.delete_baidu_creds()
    assert creds.get_baidu_creds() is None
