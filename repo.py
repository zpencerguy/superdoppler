from dagster import repository
# from jobs.baddies_jobs import baddies_ai
from jobs.magiceden_jobs import magiceden_stats_pipeline, magiceden_schedule
from jobs.twitter_jobs import prediction_tweet_job, prediction_sensor


@repository
def bots():
    return [
        # baddies_ai,
        prediction_sensor,
        prediction_tweet_job
    ]


@repository
def supperdoppler():
    return [
        magiceden_stats_pipeline,
        magiceden_schedule
    ]
