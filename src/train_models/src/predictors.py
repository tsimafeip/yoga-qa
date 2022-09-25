# # This file is copied from AllenNLP source code:
# # https://github.com/allenai/allennlp-models/blob/main/allennlp_models/generation/models/t5.py
import json

from allennlp.common import JsonDict

from allennlp.data import Instance
from allennlp.predictors import Predictor


@Predictor.register('yoga_predictor')
class Seq2SeqPredictor(Predictor):
    def predict(self, source_tokens: str) -> JsonDict:
        predicted_json_dict: JsonDict = self.predict_json({"source_tokens": source_tokens})
        predicted_json_dict["source_tokens"] = source_tokens
        predicted_json_dict["predicted_text"] = predicted_json_dict["predicted_text"].encode().decode()
        return predicted_json_dict

    def _json_to_instance(self, json_dict: JsonDict) -> Instance:
        sentence = json_dict["source_tokens"]
        return self._dataset_reader.text_to_instance(sentence)


def decode_predictions_file_to_json(pred_filepath: str, source_filepath: str, target_filepath: str):
    with open(pred_filepath, 'r', encoding='utf-8') as pred_f, \
            open(source_filepath, 'r', encoding='utf-8') as source_f, \
            open(target_filepath, 'w', encoding='utf-8') as target_f:
        for pred_line, source_line in zip(pred_f, source_f):
            pred = json.loads(pred_line)
            source = json.loads(source_line)
            target = {
                'question': source['source_tokens'],
                'gold_answer': source['target_tokens'],
                'predicted_answer': pred['predicted_text'],
                'predicted_log_probs': pred['predicted_log_probs'],
            }
            target_f.write(json.dumps(target, ensure_ascii=False) + '\n')


def decode_predictions_file_to_csv(pred_filepath: str, source_filepath: str, target_filepath: str):
    with open(pred_filepath, 'r', encoding='utf-8') as pred_f, \
            open(source_filepath, 'r', encoding='utf-8') as source_f, \
            open(target_filepath, 'w', encoding='utf-8') as target_f:

        target_f.write("question,gold_answer,predicted_answer,predicted_log_probs\n")
        for pred_line, source_line in zip(pred_f, source_f):
            pred = json.loads(pred_line)
            source = json.loads(source_line)
            source_tokens = source["source_tokens"].replace('"', "'")
            target_tokens = source["target_tokens"].replace('"', "'")
            predicted_text = pred["predicted_text"].replace('"', "'")
            values = [
                f'"{source_tokens}"',
                f'"{target_tokens}"',
                f'"{predicted_text}"',
                f'{pred["predicted_log_probs"]}',
            ]
            target_f.write(','.join(values) + '\n')
