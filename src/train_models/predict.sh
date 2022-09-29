model_path=$1
test_jsonl=$2
output=$3

# bash predict.sh archive/mt5_0.0001_batch16_accum8_seed424242/model.tar.gz data/question_to_answer/yoga_test.jsonl predictions/question_to_answer/full_yoga_test_predictions.txtg
allennlp predict "$model_path" "$test_jsonl" --predictor yoga_predictor --output-file "$output"
