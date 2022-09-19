model_path=$1
test_jsonl=$2
output=$3

# allennlp predict /home/CE/tprakap/cogs_archive/t5_cogs_0.0001_batch32_accum8_seed424242_bfs/model.tar.gz data/cogs/cogs-data-sequence/cogs_bfs_test.jsonl --predictor seq2seq_predictor --output-file cogs_test_bfs_predictions.txt
allennlp predict "$model_path" "$test_jsonl" --predictor seq2seq_predictor --output-file "$output"
