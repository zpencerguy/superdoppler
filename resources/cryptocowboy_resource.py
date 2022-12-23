import time
import requests
import pandas as pd
from urllib.parse import urlencode
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from dagster import resource


DEFAULT_TIMEOUT = 35 # seconds


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


class CCC:
    BASE_URL = "https://cryptocowboy.country/api"
    HEADERS = {
        "accept": "application/json, text/plain, */*",
        "user-agent": "Mozilla / 5.0(Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36(KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36"
    }
    RETY_STRATEGY = Retry(
        total=4,
        status_forcelist=[429, 500, 502, 503, 504],
        method_whitelist=["GET"],
        backoff_factor=5
    )
    ADAPTER = TimeoutHTTPAdapter(max_retries=RETY_STRATEGY)

    def __init__(self):
        self.session = self._get_session()
        self.data = []

    def _get_session(self):
        session = requests.session()
        session.mount("https://", self.ADAPTER)
        session.mount("http://", self.ADAPTER)
        return session

    def get_url_(self, payload):
        return "{}/predictions?{}".format(self.BASE_URL, urlencode(payload))

    def get_predictions(self, payload):
        url = self.get_url_(payload)
        print(url)
        r = self.session.get(url, headers=self.HEADERS)
        if r.status_code == 200:
            return r.json()
        else:
            return {}

    def get_data(self, payload: None):
        if not payload:
            payload = {
                "skip": 0,
                "limit": 20
            }
        batch = self.get_predictions(payload)
        self.data.append(batch)

        while len(batch) > 1:
            payload['skip'] += payload['limit']
            batch = self.get_predictions(payload)
            self.data.append(batch)
            print(f'retrieved {len(batch)} new records')
            time.sleep(0.25)

        return True


@resource
def ccc_resource():
    return CCC()


if __name__ == '__main__':
    import pandas as pd
    df_history = pd.read_csv('/Users/spencerguy/PycharmProjects/research/ccc-predictions.csv')

    client = CCC()
    payload = {
        "skip": 0,
        "limit": 20
    }
    client.get_data(payload)
    df_responses = pd.concat([pd.json_normalize(x) for x in client.data])

    df_joined = pd.concat([df_responses, df_history], ignore_index=True)
    df_complete = df_joined.drop_duplicates(subset=['id', 'predictDate'])
    df_complete.to_csv('/Users/spencerguy/PycharmProjects/research/ccc-predictions.csv')