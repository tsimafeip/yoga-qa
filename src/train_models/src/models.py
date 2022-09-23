# # This file is copied from AllenNLP source code:
# # https://github.com/allenai/allennlp-models/blob/main/allennlp_models/generation/models/t5.py

from allennlp.common import JsonDict

from allennlp.data import Instance
from allennlp.predictors import Predictor

@Predictor.register('seq2seq_predictor')
class Seq2SeqPredictor(Predictor):
    def predict(self, source_tokens: str) -> JsonDict:
        return self.predict_json({"source_tokens": source_tokens})

    def _json_to_instance(self, json_dict: JsonDict) -> Instance:
        sentence = json_dict["source_tokens"]
        return self._dataset_reader.text_to_instance(sentence)