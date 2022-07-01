from typing import List, Tuple, Iterable

import pandas as pd
from dateutil import parser

from question import YogaQuestion
from constants import ROOT_URL


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
    single_author_name = ""
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
