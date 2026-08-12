from ocr.baidu import BaiduOCRBackend


def test_parse_response_extracts_words():
    backend = BaiduOCRBackend("ak", "sk")
    payload = {"words_result": [{"words": "第一行"}, {"words": "第二行"}], "words_result_num": 2}
    assert backend._parse_response(payload) == "第一行\n第二行"


def test_parse_response_raises_on_error():
    backend = BaiduOCRBackend("ak", "sk")
    payload = {"error_code": 17, "error_msg": "open api daily request limit reached"}
    try:
        backend._parse_response(payload)
        assert False, "should raise"
    except RuntimeError as e:
        assert "17" in str(e)


def test_get_access_token_caches(monkeypatch):
    backend = BaiduOCRBackend("ak", "sk")
    calls = []

    def fake_post(url, timeout=None, **kwargs):
        calls.append(url)
        class R:
            def json(self):
                return {"access_token": "tok-1", "expires_in": 2592000}
        return R()

    monkeypatch.setattr("ocr.baidu.requests.post", fake_post)
    assert backend._get_access_token() == "tok-1"
    assert backend._get_access_token() == "tok-1"
    assert len(calls) == 1
