from dagster import op
import numpy as np


@op
def make_sentence_prompt(context, token_data):
    attributes = token_data.get('attributes')
    n = np.random.random_integers(0, len(attributes)-1)
    sentence = "{} is {}".format(attributes[n]['trait_type'], attributes[n]['value'])
    context.log.info(sentence)
    return sentence