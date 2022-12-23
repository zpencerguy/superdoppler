from dagster import job, ScheduleDefinition, DefaultScheduleStatus
from ops.magiceden_ops import get_collections, get_collection_stats, put_collection_stats
from resources import magiceden_resource, db_resource


@job(
    description="Pull Solana floor prices from MagicEden API.",
    resource_defs={
        "magiceden_resource": magiceden_resource.magiceden_resource,
        "db_resource": db_resource.db_resource.configured({"database": "superdoppler"})
    }
)
def magiceden_stats_pipeline():
    collections = get_collections()
    stats = get_collection_stats(collections)
    put_collection_stats(stats)


magiceden_schedule = ScheduleDefinition(
    job=magiceden_stats_pipeline,
    cron_schedule="*/15 * * * *",
    # default_status=DefaultScheduleStatus.RUNNING
)
