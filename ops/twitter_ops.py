from dagster import op, Output, Out, Any

@op(
    required_resource_keys={"twitter"},
    description="Posting prediction to Twitter.",
    config_schema={"template": str, "data": Any}
)
def tweet_prediction(context):
    twitter = context.resources.twitter
    data = context.op_config['data']
    template = context.op_config['template']
    for i in data:
        tweet_text = template.format(**i)
        if i['image']:
            try:
                tweet = twitter.post_tweet_with_uri_image(tweet_text, i['image'])
            except:
                tweet = twitter.post_tweet(tweet_text)
        else:
            tweet = twitter.post_tweet(tweet_text)
