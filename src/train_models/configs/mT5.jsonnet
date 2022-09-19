local epochs = 100;
local patience = 10;
local batch_size = 16;
local cuda_device = 7;

local file_prefix = "data/yoga_";
local model_name = 'google/mt5-base';

{
    numpy_seed: 0,
    pytorch_seed: 0,
    random_seed: 0,
    dataset_reader: {
        type: "yoga_seq2seq",

        tokenizer: {
            // https://docs.allennlp.org/v2.2.0/api/data/tokenizers/pretrained_transformer_tokenizer/
            type: "pretrained_transformer",
            model_name: model_name,
            // add_special_tokens: bool = True,
            // max_length: Optional[int] = None,
            // stride: int = 0,
            // tokenizer_kwargs: Optional[Dict[str, Any]] = None
        },
        source_token_indexers: {
            tokens: {
                // https://docs.allennlp.org/v2.2.0/api/data/token_indexers/pretrained_transformer_indexer/
                type: "pretrained_transformer",
                model_name: model_name,
                namespace: "source_tokens",
                max_length: 1024,
                // tokenizer_kwargs: Optional[Dict[str, Any]] = None,
            }
        },
        target_token_indexers: {
            tokens: {
                // https://docs.allennlp.org/v2.2.0/api/data/token_indexers/pretrained_transformer_indexer/
                type: "pretrained_transformer",
                model_name: model_name,
                namespace: "target_tokens",
                // max_length: int = None,
                // tokenizer_kwargs: Optional[Dict[str, Any]] = None,
            }
            // tokens: { namespace: "target_tokens" }
        },
    },

    train_data_path: file_prefix + "train.tsv",
    validation_data_path: file_prefix + "dev.tsv",
    test_data_path: file_prefix + "test.tsv",
    model: {
        type: "t5",
        model_name: model_name,
        beam_search: {
            beam_size: 3,
            max_steps: 500,
        }
        # pretrained_seq2seq:{
        #    type: "t5",
        #    model_name: model_name,
        # }
    },
    data_loader: {
        batch_sampler: {
            type: "bucket",
            batch_size: batch_size,
            padding_noise: 0.0,
            sorting_keys: ["source_tokens"]
        },
    },
    trainer: {
        num_epochs: epochs,
        patience: patience,
        num_gradient_accumulation_steps: 8,
        // validation_metric: "+exact_match_accuracy_token",
        // validation_metric: "-token_edit_distance",
        validation_metric: "-loss",
        // grad_clipping: 5.0,
        cuda_device: cuda_device,
        optimizer: {
            type: "adam",
            lr: 1e-4, # default lr 0.001
        },
        callbacks: [{type: "tensorboard"}],
        enable_default_callbacks: false
    }
}