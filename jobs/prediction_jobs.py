from dagster import job, ScheduleDefinition, DefaultScheduleStatus, sensor, RunRequest, build_resources, SkipReason, Any
from ops.prediction_ops import *
from resources import db_resource, magiceden_resource


# @job(
#     description="Get status of expired predictions and update predict table",
#     resource_defs={
#         "db_resource": db_resource.db_resource.configured({"database": "superdoppler"}),
#         "magiceden": magiceden_resource.magiceden_resource
#     }
# )
# def settle_prediction_job():
#     dfx = get_expired_predictions()
#     dfx = get_prediction_status(dfx)
#     complete = update_prediction_status(dfx)


@job(
    description="Get status of expired predictions and update predict table",
    resource_defs={
        "db_resource": db_resource.db_resource.configured({"database": "superdoppler"}),
        "magiceden": magiceden_resource.magiceden_resource
    },
    config={"ops": {
        "get_prediction_status": {
            "config": {
                "dfx": {}
            }
        },
    }}
)
def settle_prediction_job():
    dfx = get_prediction_status()
    complete = update_prediction_status(dfx)


@sensor(job=settle_prediction_job, minimum_interval_seconds=60)
def prediction_complete_sensor():
    with build_resources(
            {"db_resource": db_resource.db_resource.configured({"database": "superdoppler"})}
    ) as resources:
        db = resources.db_resource
        df = db.fetch_data_by_query("""
        select id, date, slug, direction, duration, end_price 
        from public.predict
        where status = 'active'
        """)
        df['date'] = df['date'].apply(pd.to_datetime)
        df['expired'] = df.apply(lambda x: x['date'] + timedelta(int(x['duration'])), axis=1)
        df['timestamp'] = datetime.utcnow()
        dfx = df.loc[df['expired'] <= df['timestamp']]
        if len(dfx) > 0:
            yield RunRequest(
                run_key=str(datetime.utcnow()),
                run_config={
                    "ops": {
                        "get_prediction_status": {
                            "config": {
                                "dfx": dfx.to_dict(),
                            }
                        }
                    }
                },
            )
        else:
            yield SkipReason('No recently completed predictions')


# settle_prediction_schedule = ScheduleDefinition(
#     job=settle_prediction_job,
#     cron_schedule="*/5 * * * *"
# )
