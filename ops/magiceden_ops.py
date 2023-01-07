from dagster import op, AssetMaterialization, Output
import pandas as pd
from datetime import datetime, timedelta, timezone
import time


@op(
    required_resource_keys={"db_resource"},
    description="Get list of collections from S3"
)
def get_collections(context):
    db = context.resources.db_resource
    df = db.fetch_data_by_query("select distinct slug from public.project")
    yield Output(df['slug'].to_list())


@op(
    required_resource_keys={"magiceden_resource"},
    description="Pull collection stats from API",
)
def get_collection_stats(context, symbols):
    me = context.resources.magiceden_resource
    fp_data = []

    for symbol in symbols:
        try:
            fp = me.call_stats_endpoint(symbol)
            fp_data.append(fp)
        except:
            time.sleep(0.25)
            fp = me.call_stats_endpoint(symbol)
            fp_data.append(fp)
        time.sleep(0.05)

    yield Output(fp_data)


@op(
    required_resource_keys={"magiceden_resource"},
    description="Pull activities from API",
    config_schema={"collection": str}
)
def get_collection_activities(context):
    me = context.resources.magiceden_resource
    activities = me.call_activities_endpoint(context.op_config['collection'])
    print(len(activities))
    yield Output(activities)


@op(
    required_resource_keys={"magiceden_resource"},
    description="Pull token data from API",
)
def get_token_data(context, mint_addresses):
    me = context.resources.magiceden_resource
    token_data = me.call_token_endpoint(mint_addresses)
    yield Output(token_data)


@op
def get_top_sale_mint_address(context, activities):
    df = pd.json_normalize(activities)
    top_sale = df.loc[df['type']=='buyNow'].sort_values('price', ascending=False).head(1)
    address = top_sale['tokenMint'].values[0]
    context.log.info(address)
    return address


@op(
    required_resource_keys={"db_resource"},
    description="Ingest MagicEden collection stats"
)
def put_collection_stats(context, stats):
    df_stats = pd.json_normalize(stats)
    df_stats = df_stats.loc[~df_stats['floorPrice'].isna()]
    print(df_stats.info())
    db = context.resources.db_resource

    df_ids = db.fetch_data_by_query("select slug, id from public.project")
    df_merged = df_stats.merge(df_ids, left_on='symbol', right_on='slug')

    yield AssetMaterialization(
        asset_key="MagicEden FloorPrices",
        description="Collection floor pirces",
        metadata={
            "time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "NumCollections": len(df_stats),
            "HighestFloorCollection": df_stats.sort_values("floorPrice", ascending=False).head(1)['floorPrice'].values[0],
            "HighestFloor": df_stats.sort_values("floorPrice", ascending=False).head(1)['floorPrice'].values[0]/1000000000
        },
    )

    base_stmt = """INSERT INTO public."floorPrices" (date, collection_id, marketplace_id, price, symbol) 
            VALUES ('{}', {}, {}, {}, '{}')"""
    dt = datetime.now(timezone.utc)
    stmt_list = [
        base_stmt.format(
            dt,
            x['id'],
            1,
            float(x['floorPrice'] / 1000000000),
            'SOL'
        ) for i, x in df_merged.iterrows()
    ]
    db.execute_stored_procedure(stmt_list)

    yield Output(True)
