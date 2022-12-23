# from dagster import resource
# # from transformers import GPT2LMHeadModel, GPT2Tokenizer
#
#
# class GPT2:
#     def __init__(self):
#         self.tokenizer = GPT2Tokenizer.from_pretrained('gpt2-medium')
#         self.model = GPT2LMHeadModel.from_pretrained('gpt2-medium', pad_token_id=self.tokenizer.eos_token_id)
#         self._sentence = "This is a bot I made with an NFT "
#
#     @property
#     def sentence(self):
#         print("getter method called")
#         return self._sentence
#
#     @sentence.setter
#     def sentence(self, sentence):
#         print("setter method called")
#         self._sentence = sentence
#
#     def get_output(self, max_length=30, num_beams=5):
#         input_ids = self.tokenizer.encode(self._sentence, return_tensors='pt')
#         self.output = self.model.generate(
#             input_ids,
#             max_length=max_length,
#             num_beams=num_beams,
#             no_repeat_ngram_size=2,
#             early_stopping=True
#         )
#         return self.tokenizer.decode(self.output[0], skip_special_tokens=True)
#
#
# @resource
# def gpt_resource():
#     return GPT2()
#
#
# if __name__ == '__main__':
#     tokenizer = GPT2Tokenizer.from_pretrained('gpt2-medium')
#     model = GPT2LMHeadModel.from_pretrained('gpt2-medium', pad_token_id=tokenizer.eos_token_id)
#
#     sentence = 'My eyes are covered with Sandstorm Goggles'
#
#     input_ids = tokenizer.encode(sentence, return_tensors='pt')
#
#     output = model.generate(
#         input_ids,
#         max_length=25,
#         num_beams=5,
#         no_repeat_ngram_size=3,
#         early_stopping=True
#     )
#
#     print(tokenizer.decode(output[0], skip_special_tokens=True))