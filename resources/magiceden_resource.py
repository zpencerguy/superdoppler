from urllib.parse import urlencode
from dagster import resource
import pandas as pd
import time
import re

from utils.log_util import init_logging
from utils.base_api_client import ExternalBaseApiClient
from settings import MAGICEDEN_API_KEY

logger = init_logging()


class MagicEden(ExternalBaseApiClient):
    HOST = "http://api-mainnet.magiceden.dev/v2"
    API_NAME = "MagicEden"
    KEY = MAGICEDEN_API_KEY
    AUTH_TYPE = "Bearer"
    TPM = 1200
    QPS = 20

    def call_token_endpoint(self, mint_address):
        url = "{}/tokens/{}".format(self.HOST, mint_address)
        request = self.get(url)
        return request.json()

    def call_activities_endpoint(self, symbol, payload=None):
        if payload:
            url = "{}/collections/{}/activities?{}".format(self.HOST, symbol, urlencode(payload))
        else:
            url = "{}/collections/{}/activities".format(self.HOST, symbol)
        request = self.get(url)
        return request.json()

    def call_listings_endpoint(self, symbol, payload):
        if payload:
            url = "{}/collections/{}/listings?{}".format(self.HOST, symbol, urlencode(payload))
        else:
            url = "{}/collections/{}/listings".format(self.HOST, symbol)
        request = self.get(url)

        if request.status_code == 200:
            return request.json()
        else:
            logger.debug(f"Request text: {request.text}")
            return {}

    def call_launchpad_endpoint(self, payload):
        if payload:
            url = "{}/launchpad/collections?{}".format(self.HOST, urlencode(payload))
        else:
            url = "{}/launchpad/collections".format(self.HOST)
        request = self.get(url)
        return request.json()

    def call_stats_endpoint(self, symbol):
        url = "{}/collections/{}/stats".format(self.HOST, symbol)
        request = self.get(url)
        return request.json()

    def call_collections_endpoint(self, payload):
        if payload:
            url = "{}/collections?{}".format(self.HOST, urlencode(payload))
        else:
            url = "{}/collections".format(self.HOST)
        request = self.get(url)
        return request.json()

    def get_collection_time_series(self, symbol, resolution='10m'):
        url = 'https://api-mainnet.magiceden.io/rpc/getCollectionTimeSeries/{}?edge_cache=true&resolution={}'.format(symbol, resolution)
        request = self.get(url)
        return request.json()

    def retrieve_data(self, payload, endpoint, **kwargs):
        call_endpoint_ = None
        symbol = kwargs.get('symbol')
        if endpoint == 'collections':
            call_endpoint_ = self.call_collections_endpoint
        if endpoint == 'activities':
            call_endpoint_ = self.call_activities_endpoint
        if endpoint == 'listings':
            call_endpoint_ = self.call_listings_endpoint

        if symbol:
            batch = call_endpoint_(payload, symbol)
        else:
            batch = call_endpoint_(payload)
        self.DATA.extend(batch)

        while len(batch)>0:
            payload["offset"] += 200
            batch = call_endpoint_(payload)
            self.DATA.extend(batch)
            time.sleep(0.5)

        return self.DATA


@resource(
    description="MagicEden resource to access API"
)
def magiceden_resource(init_context):
    return MagicEden()


def map_collections_to_symbol(filepath):
    """
    Use to get data for dbo.collections table
    :param filepath:
    :return: Dataframe with V2 data joined with MagicEden collection info and symbol
    """
    df_v2 = pd.read_csv(f'{filepath}/SupportedContractsSolana.csv')
    df_v2 = df_v2.loc[~df_v2['Name'].isna()]
    df_v2['name_'] = df_v2['Name'].apply(
        lambda x: " ".join([re.sub('[^A-Za-z0-9]+', '', x) for x in x.split(' ')]).lower())

    df_mec = pd.read_csv(f'{filepath}/magiceden_collections.csv')
    df_mec = df_mec.loc[~df_mec['name'].isna()]
    df_mec = df_mec.drop_duplicates('symbol')
    df_mec['name_'] = df_mec['name'].apply(
        lambda x: " ".join([re.sub('[^A-Za-z0-9]+', '', x) for x in x.split(' ')]).lower())

    df_merged = df_v2.merge(df_mec, how='left', on='name_', suffixes=('', '_me'))
    df_matched = df_merged.loc[~df_merged['symbol'].isna()]
    df_matched = df_matched.drop_duplicates('Address')
    df_matched['path'] = df_matched['Name'].apply(
        lambda x: "-".join([re.sub('[^A-Za-z0-9]+', '', x) for x in x.split(' ')]).lower())

    df_mapped = df_matched[['path', 'Address', 'Name', 'symbol']]
    df_mapped.columns = ['Path', 'Address', 'Name', 'Symbol']

    return df_mapped
