# from dagster import job
# from ops.magiceden_ops import (
#     get_collection_activities,
#     get_token_data,
#     get_top_sale_mint_address
# )
# from ops.baddie_ops import make_sentence_prompt
# from ops.gpt_ops import generate_tweet
# from resources.magiceden_resource import magiceden_resource
# from resources.gpt_resource import gpt_resource
#
#
# @job(
#     description="AI tweet from the Baddies",
#     resource_defs={
#         "magiceden_resource": magiceden_resource,
#         "gpt_resource": gpt_resource
#     },
#     config={
#         "ops": {
#             "get_collection_activities":{
#                 "config": {
#                     "collection": "y00ts"
#     }}}}
# )
# def baddies_ai():
#     activities = get_collection_activities()
#     mint_address = get_top_sale_mint_address(activities)
#     token = get_token_data(mint_address)
#     prompt = make_sentence_prompt(token)
#     tweet = generate_tweet(prompt)
#
#
