cuda=$1

batch_size=$2

lr=$3

seed=$4

dataset_name=$5

config=$6

accum_steps='8'

module_name='mt5'

root_archive_dir='archive'

params_str=$lr'_batch'$batch_size'_seed'$seed

if [ ${#cuda} != 1 ]
then
  params_str=$params_str'_multigpu'
fi

model_name=$module_name'_'$dataset_name'_'$params_str

archive_dirname=$root_archive_dir'/'$model_name

train_data_path='data/'$dataset_name'/yoga_train.tsv'
validation_data_path='data/'$dataset_name'/yoga_dev.tsv'
test_data_path='data/'$dataset_name'/yoga_test.tsv'

allennlp train \
            $config \
            --serialization-dir  $archive_dirname \
            -f --file-friendly-logging \
            -o '{"random_seed": '$seed', "numpy_seed": '$seed', "pytorch_seed": '$seed',
                 "trainer.cuda_device": '$cuda',
                 "trainer.optimizer.lr": '$lr',
                 "data_loader.batch_sampler.batch_size": '$batch_size',
                 "trainer.num_gradient_accumulation_steps": '$accum_steps',
                 "train_data_path": "'$train_data_path'",
                 "validation_data_path": "'$validation_data_path'",
                 "test_data_path": "'$test_data_path'"
                 }'
