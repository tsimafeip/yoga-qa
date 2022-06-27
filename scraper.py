import os.path
from os import listdir
from urllib import request as url_request
from time import sleep
from typing import List, Tuple, Iterable

import dateutil
import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup as bs
from tqdm import tqdm
from dateutil import parser

from question import YogaQuestion

ROOT_URL = "https://db.chgk.info"
SEED_URL = ROOT_URL + "/tour/SVOYAK"


def get_soup(page_url: str):
    try:
        response = requests.get(page_url)
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)
    soup = bs(response.content, 'html.parser')

    sleep(np.random.randint(1, 5))

    return soup


def collect_page_links(target_filename: str = 'page_links.txt', write_links_to_file: bool = True) -> List[str]:
    """
    Collects links to pages with questions or returns them from the existing file.

    Parameters
    ----------
    write_links_to_file
    target_filename

    Returns
    -------

    """
    if os.path.exists(target_filename):
        with open(target_filename) as f:
            return f.read().splitlines()

    seed_soup = get_soup(SEED_URL)

    page_links = []

    for link in seed_soup.findAll('a', href=True):
        if link.attrs.get('href', "").startswith('/tour/'):
            page_links.append(ROOT_URL + link.attrs['href'] + '/print')

    # manually crafted list of exceptions
    exceptions = {
        'https://db.chgk.info/tour//print',
        'https://db.chgk.info/tour/SVOYAK/xml/print',
        'https://db.chgk.info/tour/SVTEMA/print',
    }

    if write_links_to_file:
        with open(target_filename, 'w', encoding='utf-8') as links_file:
            for page_link in page_links:
                if page_link not in exceptions:
                    links_file.write(page_link + '\n')

    return page_links


def extract_txt_page_links(
        source_links: List[str],
        target_filename: str = 'txt_page_links.txt'
) -> List[str]:
    if os.path.exists(target_filename):
        with open(target_filename) as f:
            return f.read().splitlines()

    txt_links = []

    with open(target_filename, 'w', encoding='utf-8') as links_file:
        for link in tqdm(source_links):
            page_soup = get_soup(page_url=link)

            for link in page_soup.findAll('a', href=True):
                if link.attrs.get('href', "").startswith('/txt/'):
                    txt_link = ROOT_URL + link.attrs.get('href')
                    txt_links.append(txt_link)
                    links_file.write(txt_link + '\n')

    return txt_links


def parse_txt_page(txt_url: str):
    file = url_request.urlopen(txt_url)

    for line in file:
        decoded_line = line.decode("utf-8")
        print(decoded_line)


def extract_question_field(lines: List[str], i: int, question_value: int) -> Tuple[str, int]:
    text = []
    # while non-empty line, denoting end of the last question text, and not the next question
    stop_prefixes = {f"{val}." for val in range(question_value + 1, 6)}
    while i < len(lines) and lines[i].strip() and lines[i].strip()[:2] not in stop_prefixes:
        cur_line = lines[i].strip()
        if cur_line[:2] == f"{question_value}.":
            cur_line = cur_line[2:].strip()

        text.append(cur_line)
        i += 1

    return " ".join(text), i


def skip_empty_lines_between_blocks(lines: List[str], i: int) -> int:
    while i < len(lines) and lines[i].strip() == "":
        i += 1

    return i


def parse_single_topic(lines: List[str], i: int, tournament: str, date: str, source_url: str,
                       tournament_editor: str, tournament_author: str) \
        -> Tuple[int, Iterable[YogaQuestion], pd.DataFrame]:
    assert lines[i].startswith('Вопрос')
    i += 1
    topic_name = lines[i].strip()
    if topic_name.endswith('.'):
        topic_name = topic_name[:-1]

    questions_for_df = {
        'topic_name': [topic_name] * 5,
        'tournament': [tournament] * 5,
        'date': [date] * 5,
        'question_value': list(range(1, 6)),
        'question_text': [""] * 5,
        'answer': [""] * 5,
        'extra_answers': [""] * 5,
        'comment': [""] * 5,
        'source': [""] * 5,
        'author': [""] * 5,
        'source_url': [source_url] * 5
    }

    common_kwargs = {'topic': topic_name, 'tournament': tournament, 'date': date, 'source_url': source_url}
    topic_questions = {
        question_value: YogaQuestion(question_value=question_value, **common_kwargs)
        for question_value in range(1, 6)
    }

    i += 1

    # extract texts
    for question_value in range(1, 6):
        question_text, i = extract_question_field(lines, i, question_value)
        topic_questions[question_value].question_text = question_text
        questions_for_df['question_text'][question_value - 1] = question_text

    i = skip_empty_lines_between_blocks(lines, i)
    assert lines[i].strip() == 'Ответ:'
    i += 1
    # extract answers
    for question_value in range(1, 6):
        answer, i = extract_question_field(lines, i, question_value)

        # TODO: regex for extracting extra answers by pattern {зачет: EXTRA_ANSWER}
        # possibly, multiple extra answers, like {зачет: Голландия; Нидерланды}

        # TODO: extract comment from brackets (pattern: (...comment...) ) if it's present

        # TODO: handle [] brackets as extra answer,
        # probably, including such complex patterns as [Шоколадный] [американский] лось.

        if answer.endswith('.'):
            answer = answer[:-1]

        topic_questions[question_value].answer = answer
        questions_for_df['answer'][question_value - 1] = answer

    i = skip_empty_lines_between_blocks(lines, i)
    if i < len(lines) and lines[i].startswith('Комментарий:'):
        i += 1
        # extract comments
        for question_value in range(1, 6):
            comment, i = extract_question_field(lines, i, question_value)
            topic_questions[question_value].comment = comment
            questions_for_df['comment'][question_value - 1] = comment
        i += 1

    if i < len(lines) and lines[i].startswith('Источник:'):
        i += 1
        # extract sources
        for question_value in range(1, 6):
            source, i = extract_question_field(lines, i, question_value)
            topic_questions[question_value].source = source
            questions_for_df['source'][question_value - 1] = source

        i += 1

    single_author = False
    if i < len(lines) and lines[i] == 'Автор:':
        i += 1
        # extract single author
        if i == len(lines) - 1 or not lines[i + 1]:
            single_author = True
            single_author_name = lines[i]
        else:
            for question_value in range(1, 6):
                author, i = extract_question_field(lines, i, question_value)
                topic_questions[question_value].author = author
                questions_for_df['author'][question_value - 1] = author
    else:
        single_author = True
        if tournament_author:
            single_author_name = tournament_author
        else:
            single_author_name = tournament_editor

    if single_author:
        for question_value in range(1, 6):
            topic_questions[question_value].author = single_author_name
            questions_for_df['author'][question_value - 1] = single_author_name

    df = pd.DataFrame(
        questions_for_df,
        columns=[
            'topic_name', 'question_value', 'question_text', 'answer', 'extra_answers', 'comment', 'source', 'author',
            'tournament', 'date', 'source_url'
        ],
    )

    return i, topic_questions.values(), df


def parse_local_txt_page(filepath: str) -> Tuple[List[YogaQuestion], pd.DataFrame]:
    tournament_name = tournament_date = tournament_author = tournament_editor = ""
    source_url = ROOT_URL + '/txt/' + filepath.split('/')[-1]

    questions = []
    df = pd.DataFrame()

    with open(filepath, encoding='utf-8') as f:
        lines = f.read().splitlines()
        i = 0
        while i < len(lines):
            cur_line = lines[i]

            if cur_line == 'Чемпионат:':
                i += 1
                tournament_name = lines[i]
            elif cur_line == 'Автор:':
                i += 1
                tournament_author = lines[i]
            elif cur_line == 'Редактор:':
                i += 1
                tournament_editor = lines[i]
            elif cur_line == 'Дата:':
                i += 1
                try:
                    tournament_date = parser.parse(lines[i]).strftime("%Y-%m-%d")
                except parser._parser.ParserError as e:
                    tournament_date = lines[i]
            elif cur_line.startswith('Вопрос'):
                common_kwargs = {
                    'tournament': tournament_name,
                    'date': tournament_date,
                    'source_url': source_url,
                    'tournament_author': tournament_author,
                    'tournament_editor': tournament_editor,
                }

                i, topic_questions, topic_df = parse_single_topic(lines, i, **common_kwargs)
                df = df.append(topic_df, ignore_index=True)
                questions.extend(topic_questions)

            i += 1

    return questions, df


def download_data(txt_links: List[str], root_folder: str = 'data') -> List[str]:
    local_paths = []
    if not os.path.exists(root_folder):
        os.mkdir(root_folder)
    else:
        return [os.path.join(root_folder, f) for f in listdir(root_folder)]

    for link in tqdm(txt_links):
        page_text = get_soup(link).text
        local_filepath = os.path.join('data', link.split('/')[-1])
        with open(local_filepath, 'w', encoding='utf-8') as f:
            f.write(page_text)
        local_paths.append(local_filepath)

    return local_paths


if __name__ == '__main__':
    page_links = collect_page_links()
    txt_page_links = extract_txt_page_links(page_links)
    local_filepaths = download_data(txt_page_links)
    global_df = pd.DataFrame()
    global_questions = []
    for path in tqdm(local_filepaths):  # ['sample_file2.txt', 'sample_file.txt']:
        # print(f"Started parsing {path}...", flush=True)
        file_questions, file_df = parse_local_txt_page(path)
        global_df = global_df.append(file_df, ignore_index=True)
        global_questions.extend(file_questions)
        # print(f"Finished parsing {path}.", flush=True)

    global_df.to_csv('yoga_questions.csv', index=False)
