import json
import os.path
from collections import Counter
from typing import List

import pandas as pd

from src.train_models.src.predictors import decode_predictions_file_to_csv, decode_predictions_file_to_json

TOPIC_COL_NAME: str = 'topic_name'
QUESTION_TEXT_COL_NAME: str = 'question_text'
QUESTION_ANSWER_COL_NAME: str = 'answer'
TOURNAMENT_COL_NAME: str = 'tournament'

SEP_SYMBOL = "<SEP>"
DATA_FOLDER_PATH: str = '../data/'
YOGA_FILE_PREFIX: str = "yoga_"
SOURCE_CSV_FILENAME: str = f'{YOGA_FILE_PREFIX}questions.csv'
TSV_FILENAME: str = f'{YOGA_FILE_PREFIX}questions.tsv'

QUESTION_TO_ANSWER_FOLDER_NAME = "question_to_answer"
TOPIC_AND_QUESTION_TO_ANSWER_FOLDER_NAME = "topic_and_question_to_answer_with_sep"

PATTERN_TOURNAMENTS_FILENAME: str = 'tournaments_{}.txt'
PATTERN_DATA_FILENAME: str = 'yoga_{}.tsv'
DATA_SPLITS: List[str] = ['train', 'dev', 'test']


def split_tournaments(df: pd.DataFrame, dataset_folder: str = QUESTION_TO_ANSWER_FOLDER_NAME):
    # 62 tournaments - train data
    # 8 tournaments - test data
    # 8 tournaments - dev data
    tournaments = list(set(df[TOURNAMENT_COL_NAME]))
    train_tournaments = tournaments[:62]
    dev_tournaments = tournaments[62:70]
    test_tournaments = tournaments[70:]

    for split_name, split_tours in zip(DATA_SPLITS, [train_tournaments, dev_tournaments, test_tournaments]):
        filename = PATTERN_TOURNAMENTS_FILENAME.format(split_name)
        filepath = os.path.join(DATA_FOLDER_PATH, dataset_folder, filename)
        with open(filepath, 'w') as f:
            f.writelines([l + '\n' for l in split_tours])


def convert_tsv_test_files_to_json(file_prefix: str, test_postfix: str = 'test'):
    with open(file_prefix + f'{test_postfix}.tsv', encoding="utf-8") as input_f, \
            open(file_prefix + f'{test_postfix}.jsonl', 'w', encoding="utf-8") as out_f:
        for line in input_f:
            source_tokens, target_tokens = line.strip().split('\t')
            cur_test_entry = {
                'source_tokens': source_tokens,
                'target_tokens': target_tokens,
            }
            json_entry = json.dumps(cur_test_entry, ensure_ascii=False)
            out_f.write(json_entry + '\n')


def write_question_to_answer_tsv(target_filename: str, df: pd.DataFrame):
    target_filepath: str = os.path.join(DATA_FOLDER_PATH, QUESTION_TO_ANSWER_FOLDER_NAME, target_filename)
    with open(target_filepath, 'w') as f:
        for i in range(len(df)):
            row = df.iloc[i, :]
            f.write(f"{row[QUESTION_TEXT_COL_NAME]}\t{row[QUESTION_ANSWER_COL_NAME]}\n")


def split_question_to_answer_data(df: pd.DataFrame):
    for split_name in DATA_SPLITS:
        tournaments_filename = PATTERN_TOURNAMENTS_FILENAME.format(split_name)
        tournaments_filepath = os.path.join(DATA_FOLDER_PATH, tournaments_filename)
        with open(tournaments_filepath) as f:
            tournaments = {l.strip() for l in f.readlines()}
            write_question_to_answer_tsv(
                target_filename=PATTERN_DATA_FILENAME.format(split_name),
                df=df[df[TOURNAMENT_COL_NAME].isin(tournaments)],
            )


def write_question_to_answer(df: pd.DataFrame):
    write_question_to_answer_tsv(target_filename=TSV_FILENAME, df=df)
    split_question_to_answer_data(df)
    convert_tsv_test_files_to_json(
        file_prefix=os.path.join(
            DATA_FOLDER_PATH,
            QUESTION_TO_ANSWER_FOLDER_NAME,
            YOGA_FILE_PREFIX,
        ))

def write_tsv(target_filename: str, target_df: pd.DataFrame, dataset_folder: str):
    target_filepath: str = os.path.join(
        DATA_FOLDER_PATH,
        dataset_folder,
        target_filename,
    )
    target_df.to_csv(target_filepath, sep='\t', index=False, header=False)

def write_topic_and_question_to_answer_tsv(target_filename: str, df: pd.DataFrame):
    target_filepath: str = os.path.join(
        DATA_FOLDER_PATH,
        TOPIC_AND_QUESTION_TO_ANSWER_FOLDER_NAME,
        target_filename,
    )
    with open(target_filepath, 'w') as f:
        for i in range(len(df)):
            row = df.iloc[i, :]
            f.write(f"{row[TOPIC_COL_NAME]} {SEP_SYMBOL} {row[QUESTION_TEXT_COL_NAME]}\t{row[QUESTION_ANSWER_COL_NAME]}\n")

def split_topic_and_question_to_answer_data(df: pd.DataFrame):
    for split_name in DATA_SPLITS:
        tournaments_filename = PATTERN_TOURNAMENTS_FILENAME.format(split_name)
        tournaments_filepath = os.path.join(DATA_FOLDER_PATH, tournaments_filename)
        with open(tournaments_filepath) as f:
            tournaments = {l.strip() for l in f.readlines()}
            write_topic_and_question_to_answer_tsv(
                target_filename=PATTERN_DATA_FILENAME.format(split_name),
                df=df[df[TOURNAMENT_COL_NAME].isin(tournaments)],
            )

def write_topic_and_question_to_answer(df: pd.DataFrame):
    # write_tsv(target_filename=TSV_FILENAME, target_df=df, dataset_folder=TOPIC_AND_QUESTION_TO_ANSWER_FOLDER_NAME)
    split_topic_and_question_to_answer_data(df)
    convert_tsv_test_files_to_json(
        file_prefix=os.path.join(
            DATA_FOLDER_PATH,
            TOPIC_AND_QUESTION_TO_ANSWER_FOLDER_NAME,
            YOGA_FILE_PREFIX,
        ))


if __name__ == "__main__":
    df = pd.read_csv(os.path.join(DATA_FOLDER_PATH, SOURCE_CSV_FILENAME))

    print(f"Col Names: {df.columns.values}")
    print(f"Dataset Size: {len(df)}")
    print(f"Tournaments Number: {len(set(df[TOURNAMENT_COL_NAME]))}")
    # split_tournaments(df)
    # write_question_to_answer(df)
    # write_topic_and_question_to_answer(df)

    # decode_predictions_file_to_json(
    #     source_filepath='../data/question_to_answer/yoga_test.jsonl',
    #     pred_filepath='../full_yoga_test_predictions.txt',
    #     target_filepath='../predictions_decoded.txt'
    # )
    # decode_predictions_file_to_csv(
    #     source_filepath='../data/topic_and_question_to_answer_with_sep/yoga_test.jsonl',
    #     pred_filepath='../topic_and_question_yoga_test_predictions.txt',
    #     target_filepath='../predictions_decoded.csv'
    # )
    df = pd.read_csv('../predictions_decoded.csv')
    sorted_df = df.sort_values(by="predicted_log_probs", ascending=False)
    sorted_df.to_csv('../predictions_decoded_sorted.csv', index=False)
    # sorted_df = pd.read_csv('../predictions_decoded_sorted.csv', index_col=False)
    # print(sorted_df.columns)
    #
    correct_answers_df = df[df['gold_answer'] == df['predicted_answer']]

    exact_match = len(correct_answers_df)

    print(f'Exact match: {exact_match}/{len(sorted_df)}. Accuracy: {exact_match/len(sorted_df)}.')
    unique_answers = Counter(df['predicted_answer'])
    print(unique_answers.most_common())
    print(correct_answers_df)
    print(len(unique_answers))


