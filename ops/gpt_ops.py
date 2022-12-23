from dagster import op


@op(
    required_resource_keys={"gpt_resource"}
)
def generate_tweet(context, sentence_prompt):
    gpt = context.resources.gpt_resource
    gpt.sentence = sentence_prompt
    tweet = gpt.get_output()
    context.log.info(tweet)
    return tweet