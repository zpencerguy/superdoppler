from dagster import op
import pandas as pd


@op
def get_history():
    df_history = pd.read_csv('/Users/spencerguy/PycharmProjects/solana_automation/data/ccc-predictions-hist.csv')
    return df_history


@op(
    description="Get latest predictions from API",
    config_schema={"skip": int, "limit": int},
    required_resource_keys={"cryptocowboy"}
)
def get_predictions(context):
    skip = context.op_config['skip']
    limit = context.op_config['limit']
    payload = {"skip": skip, "limit": limit}
    ccc = context.resources.cryptocowboy
    data = ccc.get_predictions(payload)
    return data


@op(
    description="Merge new data with history and save to disk"
)
def merge_predictions(data, df_history):
    hist_count = len(df_history)
    df_new = pd.json_normalize(data)
    df_merged = pd.concat([df_new, df_history], ignore_index=True)
    df_complete = df_merged.drop_duplicates(subset=['id', 'predictDate'])
    delta = len(df_new)
    print(f"Added {delta} new predictions")
    df_complete.to_csv('/Users/spencerguy/PycharmProjects/research/ccc-predictions-hist.csv')
    return True