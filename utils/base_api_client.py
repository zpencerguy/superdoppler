import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from requests.exceptions import RetryError
from urllib3.exceptions import MaxRetryError
import time
import base64

import settings
from utils.log_util import init_logging

logger = init_logging('ExternalAPI')

DEFAULT_TIMEOUT = 10 # seconds


class TimeoutHTTPAdapter(HTTPAdapter):
    def __init__(self, *args, **kwargs):
        self.timeout = DEFAULT_TIMEOUT
        if "timeout" in kwargs:
            self.timeout = kwargs["timeout"]
            del kwargs["timeout"]
        super().__init__(*args, **kwargs)

    def send(self, request, **kwargs):
        timeout = kwargs.get("timeout")
        if timeout is None:
            kwargs["timeout"] = self.timeout
        return super().send(request, **kwargs)


def retry_on_error(func):
    def wrapper(self, *args, **kwargs):
        response = func(self, *args, **kwargs)
        if response.status_code == 401:
            response = func(self, *args, **kwargs)
        if response.status_code == 495:
            response = func(self, *args, **kwargs)
        if response.status_code == 500:
            print(f'Server error, sleeping and trying again once')
            time.sleep(1)
            response = func(self, *args, **kwargs)
        if response.status_code == 429:
            print('Throttled, sleeping and trying again')
            time.sleep(1)
            response = func(self, *args, **kwargs)
        if response.status_code == 400:
            raise ValueError(response.text)
        if response.status_code == 401:
            raise requests.exceptions.HTTPError(response.text)
        if response.status_code == 403:
            raise ConnectionError("The server blocked access.")
        if response.status_code == 408:
            time.sleep(1)
            response = func(self, *args, **kwargs)
        if response.status_code == 504:
            raise TimeoutError("The server reported a gateway time-out error.")
        return response
    return wrapper


class ExternalBaseApiClient(object):
    API_NAME = None
    HOST = None
    KEY = None
    AUTH_TYPE = "Basic"
    USER = None
    retry_strategy = Retry(
        total=3,
        status_forcelist=[429, 500, 502, 503, 504],
        method_whitelist=["GET"],
        backoff_factor=4
    )

    ADAPTER = TimeoutHTTPAdapter(max_retries=retry_strategy)

    def __init__(self):
        self.timeout = 10
        self._get_session()

    def _get_session(self):
        self.session = requests.session()
        self.session.mount("https://", self.ADAPTER)
        self.session.mount("http://", self.ADAPTER)

    def _get_headers(self, **kwargs):
        if self.AUTH_TYPE == 'X-API-KEY':
            return {
            "Accept": "application/json",
            "X-API-KEY": self.KEY
        }
        if self.AUTH_TYPE == 'BASIC':
            return {
                "Accept": "application/json",
                "Authorization": f"{self.AUTH_TYPE} {self.KEY}"
            }
        if self.AUTH_TYPE == 'Basic':
            key = self.encode_basic_auth(f"{self.USER}:{self.KEY}")
            return {
                "Accept": "application/json",
                "Authorization": f"{self.AUTH_TYPE} {key}"
            }
        if self.AUTH_TYPE == 'Bearer':
            return {
                "Accept": "application/json",
                "Authorization": f"Bearer {self.KEY}"
            }
        if self.AUTH_TYPE == 'Blobr':
            return {
                "X-BLOBR-KEY": self.KEY,
                "Accept": "application/json",
            }
        else:
            return {
                "Accept": "application/json",
            }

    def encode_basic_auth(self, message):
        message_bytes = message.encode('ascii')
        base64_bytes = base64.b64encode(message_bytes)
        return base64_bytes.decode('ascii')

    @retry_on_error
    def _request(self, request_method, url, payload=None):
        if request_method == "get":
            return self.session.get(url, headers=self._get_headers())
        else:
            return self.session.post(url, headers=self._get_headers(), json=payload)

    def get(self, url):
        return self._request("get", url)

    def post(self, url, payload):
        return self._request("post", url, payload)

    def _validate_call(self, request):
        if request.status_code == 400:
            raise ValueError(request.text)
        elif request.status_code == 401:
            raise requests.exceptions.HTTPError(request.text)
        elif request.status_code == 403:
            raise ConnectionError("The server blocked access.")
        elif request.status_code == 495:
            raise requests.exceptions.SSLError("SSL certificate error")
        elif request.status_code == 504:
            raise TimeoutError("The server reported a gateway time-out error.")
        if request.status_code != 200:
            raise Exception(500, f"{self.API_NAME} responded with error code.")