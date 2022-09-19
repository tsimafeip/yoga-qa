import json
import os.path
from typing import List

import pandas as pd

QUESTION_TEXT_COL_NAME: str = 'question_text'
QUESTION_ANSWER_COL_NAME: str = 'answer'
TOURNAMENT_COL_NAME: str = 'tournament'

CSV_PATH: str = '../data/yoga_questions.csv'
TSB_PATH: str = '../data/yoga_questions.tsv'

PATTERN_TOURNAMENTS_PATH: str = '../data/tournaments_{}.txt'
PATTERN_DATA_PATH: str = '../data/yoga_{}.tsv'
DATA_SPLITS: List[str] = ['train', 'dev', 'test']


def write_tsv(target_filepath: str, df: pd.DataFrame):
    with open(target_filepath, 'w') as f:
        question_answer_pairs = df[[QUESTION_TEXT_COL_NAME, 'answer']]
        for i in range(len(df)):
            row = question_answer_pairs.iloc[i, :]
            f.write(f"{row[QUESTION_TEXT_COL_NAME]}\t{row[QUESTION_ANSWER_COL_NAME]}\n")


def split_tournaments(df: pd.DataFrame):
    # 62 tournaments - train data
    # 8 tournaments - test data
    # 8 tournaments - dev data
    tournaments = list(set(df[TOURNAMENT_COL_NAME]))
    train_tournaments = tournaments[:62]
    dev_tournaments = tournaments[62:70]
    test_tournaments = tournaments[70:]

    for split_name, split_tours in zip(DATA_SPLITS, [train_tournaments, dev_tournaments, test_tournaments]):
        with open(PATTERN_TOURNAMENTS_PATH.format(split_name), 'w') as f:
            f.writelines([l + '\n' for l in split_tours])


def split_data(df: pd.DataFrame):
    for split_name in DATA_SPLITS:
        with open(PATTERN_TOURNAMENTS_PATH.format(split_name)) as f:
            tournaments = {l.strip() for l in f.readlines()}
            write_tsv(
                target_filepath=PATTERN_DATA_PATH.format(split_name),
                df=df[df[TOURNAMENT_COL_NAME].isin(tournaments)],
            )


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


if __name__ == "__main__":
    df = pd.read_csv(CSV_PATH)

    print(f"Col Names: {df.columns.values}")
    print(f"Dataset Size: {len(df)}")
    print(f"Tournaments Number: {len(set(df[TOURNAMENT_COL_NAME]))}")

    # write_tsv(TSV_PATH, df=df)
    # split_tournaments(df)
    # split_data(df)
    convert_tsv_test_files_to_json(file_prefix=os.path.join("..", "data", "yoga_"))
