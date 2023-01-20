import time
from datetime import timedelta, datetime
from dagster import op, Output, Out, Any, AssetMaterialization
import pandas as pd


def get_status(end_price, fp, direction):
    status = ''
    if direction == 'up':
        if fp >= end_price:
            status = 'correct'
        elif fp < end_price:
            status = 'incorrect'
    if direction == 'down':
        if fp < end_price:
            status = 'correct'
        elif fp >= end_price:
            status = 'incorrect'
    return status


@op(
    description="Get active predictions from database",
    required_resource_keys={"db_resource"}
)
def get_expired_predictions(context):
    db = context.resources.db_resource
    df = db.fetch_data_by_query("""
    select id, date, slug, direction, duration, end_price 
    from public.predict
    where status = 'active'
    """)
    df['date'] = df['date'].apply(pd.to_datetime)
    df['expired'] = df.apply(lambda x: x['date'] + timedelta(int(x['duration'])), axis=1)
    df['timestamp'] = datetime.utcnow()
    dfx = df.loc[df['expired'] <= df['timestamp']]
    return dfx


@op(
    description="Get prediction outcome based on MR API floor price",
    required_resource_keys={"magiceden"}
)
def get_prediction_status(context, dfx):
    slugs = dfx['slug'].unique()
    me = context.resources.magiceden
    responses = []
    for x in slugs:
        r = me.call_stats_endpoint(x)
        responses.append(r)
        time.sleep(0.2)
    dfr = pd.json_normalize(responses)
    dfr['floorPrice'] = dfr['floorPrice'] * 0.000000001
    dfr = dfr.drop_duplicates('symbol')
    fp_map = dfr.set_index('symbol')['floorPrice'].to_dict()
    dfx['fp'] = dfx['slug'].map(fp_map)
    dfx['status'] = dfx.apply(lambda x: get_status(x['end_price'], x['fp'], x['direction']), axis=1)
    return dfx


@op(
    required_resource_keys={"db_resource"},
    description="Updating prediction status",
    # config_schema={"template": str, "data": Any}
)
def update_prediction_status(context, dfx):
    db = context.resources.db_resource
    settled = 0
    for i, row in dfx.iterrows():
        x = db.update_status(row['id'], row['status'])
        settled += x

    yield AssetMaterialization(
        asset_key="Updated Predictions",
        description="Number of predictions completed and updated",
        metadata={
            "settled": settled
        },
    )

    yield Output(True)