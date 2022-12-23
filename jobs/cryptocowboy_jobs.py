from dagster import job
from ops.cryptocowboy_ops import *
from resources.cryptocowboy_resource import ccc_resource


@job(
    description="Archive Crypto Cowboy Country predictions",
    resource_defs={
        "cryptocowboy": ccc_resource
    },
    config={
        "ops": {
            "get_predictions":{
                "config": {
                    "skip": 0,
                    "limit": 50
    }}}}
)
def predictions_archive_job():
    df_history = get_history()
    predictions = get_predictions()
    merge_predictions(predictions, df_history)


