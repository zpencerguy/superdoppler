from dagster import repository
# from jobs.baddies_jobs import baddies_ai
from jobs.magiceden_jobs import magiceden_stats_pipeline, magiceden_schedule


@repository
def bots():
    return [
        # baddies_ai
    ]


@repository
def supperdoppler():
    return [
        magiceden_stats_pipeline,
        magiceden_schedule
    ]
