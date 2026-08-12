import base64
import time

import requests

from ocr.base import OCRBackend

TOKEN_URL = "https://aip.baidubce.com/oauth/2.0/token"
OCR_URL = "https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic"


class BaiduOCRBackend(OCRBackend):
    _name = "baidu"

    def __init__(self, api_key: str, secret_key: str):
        self._api_key = api_key
        self._secret_key = secret_key
        self._token = None
        self._token_expiry = 0.0

    @property
    def name(self) -> str:
        return self._name

    def _get_access_token(self) -> str:
        now = time.time()
        if self._token and now < self._token_expiry:
            return self._token
        resp = requests.post(TOKEN_URL, timeout=15, params={
            "grant_type": "client_credentials",
            "client_id": self._api_key,
            "client_secret": self._secret_key,
        })
        data = resp.json()
        if "access_token" not in data:
            raise RuntimeError(f"token request failed: {data.get('error', 'unknown')}")
        self._token = data["access_token"]
        self._token_expiry = now + int(data.get("expires_in", 2592000)) - 60
        return self._token

    def _parse_response(self, payload: dict) -> str:
        if "error_code" in payload:
            raise RuntimeError(f"baidu ocr error {payload['error_code']}: {payload.get('error_msg')}")
        words = [item["words"] for item in payload.get("words_result", [])]
        return "\n".join(words)

    def recognize(self, image_path: str) -> str:
        with open(image_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")
        token = self._get_access_token()
        resp = requests.post(OCR_URL, timeout=30, params={"access_token": token}, data={"image": encoded})
        return self._parse_response(resp.json())
