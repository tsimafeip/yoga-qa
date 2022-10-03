model_path=$1
test_jsonl=$2
output=$3

allennlp predict "$model_path" "$test_jsonl" --predictor yoga_predictor --output-file "$output"
