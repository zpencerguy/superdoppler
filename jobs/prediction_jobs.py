from dagster import job, ScheduleDefinition, DefaultScheduleStatus, sensor, RunRequest, build_resources, SkipReason
from ops.prediction_ops import *
from resources import db_resource, magiceden_resource


@job(
    description="Get status of expired predictions and update predict table",
    resource_defs={
        "db_resource": db_resource.db_resource.configured({"database": "superdoppler"}),
        "magiceden": magiceden_resource.magiceden_resource
    }
)
def settle_prediction_job():
    dfx = get_expired_predictions()
    dfx = get_prediction_status(dfx)
    complete = update_prediction_status(dfx)


settle_prediction_schedule = ScheduleDefinition(
    job=settle_prediction_job,
    cron_schedule="*/5 * * * *"
)
