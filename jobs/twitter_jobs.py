from dagster import job, ScheduleDefinition, DefaultScheduleStatus, sensor, RunRequest, build_resources, SkipReason
from ops.twitter_ops import *
from resources import twitter_resource, db_resource


@job(
    description="Super Forecaster predictions Twitter bot",
    resource_defs={
        "twitter": twitter_resource.twitter,
    },
    config={"ops": {
        "tweet_prediction": {
            "config": {
                "template": "{name} was just predicted to go {direction} in price in {duration} days by a Super Forecaster",
                "data": [{"name": "Cloudz", 'direction': 'up', 'duration': '3'}]
            }
        },
    }}
)
def prediction_tweet_job():
    tweet_prediction()


@sensor(job=prediction_tweet_job, minimum_interval_seconds=60)
def cardano_bot_sensor():
    with build_resources(
            {"db_resource": db_resource.db_resource.configured({"database": "superdoppler"})}
    ) as resources:
        db = resources.db_resource

        df = db.fetch_data_by_query(
            """select p.id, name, direction, duration
            from predict p
            inner join project p2
                on p.slug = p2.slug 
            order by date desc
            limit 5"""
        )
        if len(df) > 0:
            template = "{name} was just predicted to go {direction} in price in {duration} days by a Super Forecaster"
            for i, row in df.iterrows():
                tweet_data_ = {}
                tweet_data_['name'] = row['name']
                tweet_data_['direction'] = row['direction']
                tweet_data_['duration'] = row['duration']

                run_key = f"{row['id']}"
                yield RunRequest(
                    run_key=run_key,
                    run_config={
                        "ops": {
                            "tweet_prediction": {
                                "config": {
                                    "template": template,
                                    "data": [tweet_data_]
                                }
                            }
                        }
                    },
                )
        else:
            yield SkipReason('No new predictions')