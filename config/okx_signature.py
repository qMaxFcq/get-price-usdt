from requests import Request, Session, Response
from urllib.parse import urlencode
from json import dumps
import hmac
from base64 import standard_b64encode
from typing import Optional, Dict, Any
from arrow import utcnow
from pandas import DataFrame
from os import getcwd, getenv
import sys
########### Local Import ###########
from helper.json_obj import json_obj

sys.path.append(getcwd())

class OkxMerchant:
    def __init__(self, api_key=None, api_secret=None, api_passphrase=None):
        self._api_key = api_key
        self._api_secret = api_secret
        self._api_passphrase = api_passphrase
        self._base_url = "https://www.okx.com/api/v5"
        self._session = Session()

    def _generate_signature(self, timestamp: str, request: Request):
        try:
            auth: str = f"{ timestamp }{ request.method }/api/v5{ request.url }"
            auth += "" if not request.params else f"?{urlencode(request.params)}"
            auth += "" if not request.json else dumps(request.json)
            secret: bytes = (
                b"" if not self._api_secret else self._api_secret.encode(
                    "utf-8")
            )
            binary: bytes = hmac.new(
                secret, auth.encode("utf-8"), digestmod="sha256"
            ).digest()
            signature: str = standard_b64encode(binary).decode("utf-8")
            return signature
        except Exception as e:
            print(f"Error generating signature: {e}")
        return None

    def _get(
        self, path: str, params: Optional[Dict[str, Any]] = None, auth_request=False
    ) -> Any:
        return self._request("GET", path, params=params, auth_request=auth_request)

    def _post(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        auth_request=False,
    ) -> Any:
        return self._request(
            "POST", path, params=params, json=json, auth_request=auth_request
        )

    def _request(self, method: str, path: str, auth_request: bool, **kwargs) -> Any:
        request = Request(method, path, **kwargs)
        if auth_request:
            self._sign_request(request)
        response = self._session.send(request.prepare())
        return self._process_response(response)

    def _sign_request(self, request: Request) -> None:
        timestamp: str = utcnow().format("YYYY-MM-DD[T]HH:mm:ss.SSS[Z]")
        request.headers["OK-ACCESS-KEY"] = self._api_key
        request.headers["OK-ACCESS-PASSPHRASE"] = self._api_passphrase
        request.headers["OK-ACCESS-SIGN"] = self._generate_signature(
            request=request, timestamp=timestamp
        )
        request.headers["OK-ACCESS-TIMESTAMP"] = timestamp
        request.url = self._base_url + request.url

    def _process_response(self, response: Response) -> Any:
        try:
            data = response.json()
        except ValueError:
            response.raise_for_status()
            data = {}
        return data

    def ad_marketplace_list(self) -> DataFrame:
        url = "/p2p/ad/marketplace-list"
        params = {
            "cryptoCurrency": "USDT",
            "fiatCurrency": "THB",
            "paymentMethod": "bank",
        }
        return self._get(url, params=params, auth_request=True)

    def order_list(self, page_index: int = 1, page_size: int = 100) -> DataFrame:
        url = "/p2p/order/list"
        params = {"orderType": "all",
                  "pageIndex": page_index, "pageSize": page_size}
        return json_obj(self._get(url, params=params, auth_request=True))

    def order_id(self) -> DataFrame:
        url = "/p2p/order"
        params = {"orderId": "230711172232487"}
        return self._get(url, params=params, auth_request=True)

    def user_info(self) -> DataFrame:
        url = "/p2p/user/basic-info"
        return self._get(url, auth_request=True)

    def user_balance(self) -> DataFrame:
        url = "/p2p/user/balance"
        params = {
            "currencySymbol": "USDT",
        }
        return self._get(url, params=params, auth_request=True)

    def ad_detail(self, adId: str) -> DataFrame:
        url = "/p2p/ad"
        params = {
            "adId": adId
        }

        return self._get(url, params=params, auth_request=True)

    def update_price(self, adId: str, unitPrice: str) -> DataFrame:
        url = "/p2p/ad/update"
        payload = {
            "adId": adId,
            "unitPrice": unitPrice
        }

        return self._post(url, json=payload, auth_request=True)
