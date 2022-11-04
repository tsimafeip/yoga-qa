from typing import List, Tuple, Iterable, Dict, Any

import pandas as pd
from dateutil import parser

from question import YogaQuestion
from constants import ROOT_URL


def extract_question_field(lines: List[str], i: int, question_value: int) -> Tuple[str, int]:
    text = []
    # while non-empty line, denoting end of the last question text, and not the next question
    question_prefix_1 = f"{question_value}."
    question_prefix_2 = f"{question_value}0."
    stop_prefixes = set()
    while i < len(lines) and lines[i].strip():
        cur_line = lines[i].strip()
        if cur_line[:2] in stop_prefixes or cur_line[:3] in stop_prefixes:
            break

        if cur_line.startswith(question_prefix_1):
            # For example: 2, 3, 4, 5
            stop_prefixes = {f"{val}." for val in range(question_value + 1, 15)}
            cur_line = cur_line[2:].strip()
        elif cur_line.startswith(question_prefix_2):
            # For example: 20, 30, 40, 50
            stop_prefixes = {f"{val}." for val in range(10 * (question_value + 1), 151, 10)}
            cur_line = cur_line[3:].strip()

        text.append(cur_line)
        i += 1

    return " ".join(text), i


def skip_empty_lines_between_blocks(lines: List[str], i: int) -> int:
    while i < len(lines) and lines[i].strip() == "":
        i += 1

    return i


def _extract_extra_answers(answer: str) -> Tuple[str, List[str], List[str]]:
    extra_positive_keyword = 'зачет: '
    hard_negative_keyword = 'незачет:'
    extra_pos_start_i = answer.find(extra_positive_keyword)
    hard_neg_start_i = answer.find(hard_negative_keyword)

    extra_positives = []
    hard_negatives = []

    if extra_pos_start_i != -1 and hard_neg_start_i == -1:
        extra_answer = answer[extra_pos_start_i + len(extra_positive_keyword):]
        extra_answer = extra_answer.replace('так уж и быть, ', "").replace('так уж и быть', "")
        answer = answer[:extra_pos_start_i - 1]
        extra_positives = extra_answer.split(';') if ';' in extra_answer else extra_answer.split(',')
    elif hard_neg_start_i != -1:
        hard_negatives = answer[hard_neg_start_i + len(hard_negative_keyword) + 1:].split(',')
        answer = answer[:hard_neg_start_i]
        if extra_positive_keyword in answer:
            if answer.endswith('; '):
                answer = answer[:-2]
            answer, extra_positives, _ = _extract_extra_answers(answer)

    return answer, extra_positives, hard_negatives


def set_question_field(field_name: str, field_value: str, question_value: int,
                       topic_questions: Dict[int, YogaQuestion], df: Dict[str, Any]):
    setattr(topic_questions[question_value], field_name, field_value)
    df[field_name][question_value - 1] = field_value


def extract_and_remove_brackets_content(answer: str, opening_bracket: str) -> Tuple[str, List[str], List[str]]:
    # TODO: improve extracting extra answers from patterns like this: '[момоти] тамба [одиннадцатый]'
    assert opening_bracket in {'{', '(', '['}

    opening_to_closing_bracket = {'{': '}', '(': ')', '[': ']'}

    expanded_answer_start = answer.find(opening_bracket)
    expanded_answer_end = 1 + answer.find(opening_to_closing_bracket[opening_bracket])

    expanded_answer_word = answer[expanded_answer_start + 1:expanded_answer_end - 1]
    _, local_extra_positives, local_hard_negatives = _extract_extra_answers(expanded_answer_word)
    answer = answer[:expanded_answer_start] + answer[expanded_answer_end + 1:]
    return answer, local_extra_positives, local_hard_negatives


def process_answer(answer: str) -> Tuple[str, List[str], List[str], str]:
    answer = answer.replace('"', "").replace("'", "").replace('.', "").lower()
    extra_positives = []
    hard_negatives = []
    answer_prefix = extracted_comment = ""

    if answer.startswith('['):
        '''
        Fix:
        '[момоти] тамба [одиннадцатый]'
        ''[площадь] рынок {зачет: рынковая [площадь]}'
        '''
        extra_end = answer.find("]")
        answer_prefix = answer[1:extra_end]
        answer = answer[extra_end + 2:]

    if '{' in answer:
        answer, local_extra_positives, local_hard_negatives = \
            extract_and_remove_brackets_content(answer, opening_bracket='{')
        extra_positives.extend(local_extra_positives)
        hard_negatives.extend(local_hard_negatives)

    while '[' in answer:
        answer, local_extra_positives, local_hard_negatives = \
            extract_and_remove_brackets_content(answer, opening_bracket='[')
        extra_positives.extend(local_extra_positives)
        hard_negatives.extend(local_hard_negatives)

    answer, extracted_extra_pos, extracted_hard_neg = _extract_extra_answers(answer)
    extra_positives.extend(extracted_extra_pos)
    hard_negatives.extend(extracted_hard_neg)

    if '(' in answer:
        comment_start = answer.find("(")
        comment_end = answer.rfind(")")
        comment = answer[comment_start + 1:comment_end]
        # +1 to skip extra space
        if comment_end + 1 == len(answer):
            answer = answer[:comment_start - 1]
            extracted_comment = comment
        elif comment_start == 0:
            answer = answer[comment_end + 2:]
            extra_answer = comment + ' ' + answer
            extra_positives.append(extra_answer)
        else:
            for alternative_start in comment.split(','):
                extra_answer = alternative_start + ' ' + answer[comment_end + 2:]
                extra_positives.append(extra_answer)
            answer = answer[:comment_start - 1] + ' ' + answer[comment_end + 2:]

    answer = answer.strip()

    if answer_prefix:
        extra_answer = answer_prefix + ' ' + answer
        extra_positives.append(extra_answer)

    answer = answer\
        .replace('(', "").replace(')', "")\
        .replace('[', "").replace(']', "")\
        .replace('{', "").replace('}', "")

    return answer, extra_positives, hard_negatives, extracted_comment


def parse_single_topic(lines: List[str], i: int, tournament: str, date: str, source_url: str,
                       tournament_editor: str, tournament_author: str) \
        -> Tuple[int, Iterable[YogaQuestion], pd.DataFrame]:
    assert lines[i].startswith('Вопрос')
    i += 1
    topic_name = []
    counter = 0
    while not (lines[i+1].strip().startswith('1.') or lines[i+1].strip().startswith('10.')):
        topic_name.append(lines[i].strip())
        i += 1
        counter += 1

    topic_name.append(lines[i])
    topic_name = ' '.join(topic_name)
    if topic_name.endswith('.'):
        topic_name = topic_name[:-1]

    i += 1

    # extract texts
    question_value_to_text = {}
    question_value = 1
    while True:
        question_text, i = extract_question_field(lines, i, question_value)
        question_value_to_text[question_value] = question_text
        if not lines[i].strip():
            break
        question_value += 1

    questions_in_topic = len(question_value_to_text)

    questions_for_df = {
        'topic_name': [topic_name] * questions_in_topic,
        'tournament': [tournament] * questions_in_topic,
        'date': [date] * questions_in_topic,
        'question_value': list(range(1, questions_in_topic+1)),
        'question_text': [""] * questions_in_topic,
        'answer': [""] * questions_in_topic,
        'extra_positives': [""] * questions_in_topic,
        'hard_negatives': [""] * questions_in_topic,
        'comment': [""] * questions_in_topic,
        'source': [""] * questions_in_topic,
        'author': [""] * questions_in_topic,
        'source_url': [source_url] * questions_in_topic
    }

    common_kwargs = {'topic': topic_name, 'tournament': tournament, 'date': date, 'source_url': source_url}
    topic_questions = {
        question_value: YogaQuestion(question_value=question_value, **common_kwargs)
        for question_value in range(1, questions_in_topic+1)
    }

    for question_value, question_text in question_value_to_text.items():
        set_question_field(field_name='question_text', field_value=question_text, question_value=question_value,
                           topic_questions=topic_questions, df=questions_for_df)

    i = skip_empty_lines_between_blocks(lines, i)
    assert lines[i].strip() == 'Ответ:'
    i += 1
    # extract answers
    for question_value in range(1, questions_in_topic+1):
        answer, i = extract_question_field(lines, i, question_value)
        answer, extra_positives, hard_negatives, extracted_comment = process_answer(answer)

        set_question_field(field_name='answer', field_value=answer, question_value=question_value,
                           topic_questions=topic_questions, df=questions_for_df)

        extra_positives_str = ";".join([process_answer(pos)[0] for pos in extra_positives if len(pos.split()) <= 5])
        set_question_field(field_name='extra_positives', field_value=extra_positives_str, question_value=question_value,
                           topic_questions=topic_questions, df=questions_for_df)

        hard_negatives_str = ";".join([process_answer(neg)[0] for neg in hard_negatives if len(neg.split()) <= 5])
        set_question_field(field_name='hard_negatives', field_value=hard_negatives_str, question_value=question_value,
                           topic_questions=topic_questions, df=questions_for_df)

    i = skip_empty_lines_between_blocks(lines, i)
    if i < len(lines) and lines[i].startswith('Комментарий:'):
        i += 1
        # extract comments
        for question_value in range(1, questions_in_topic+1):
            comment, i = extract_question_field(lines, i, question_value)
            set_question_field(field_name='comment', field_value=comment, question_value=question_value,
                               topic_questions=topic_questions, df=questions_for_df)
        i += 1

    if i < len(lines) and lines[i].startswith('Источник:'):
        i += 1
        # extract sources
        for question_value in range(1, questions_in_topic+1):
            source, i = extract_question_field(lines, i, question_value)
            set_question_field(field_name='source', field_value=source, question_value=question_value,
                               topic_questions=topic_questions, df=questions_for_df)

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
                set_question_field(field_name='author', field_value=author, question_value=question_value,
                                   topic_questions=topic_questions, df=questions_for_df)
    else:
        single_author = True
        if tournament_author:
            single_author_name = tournament_author
        else:
            single_author_name = tournament_editor

    if single_author:
        for question_value in range(1, questions_in_topic+1):
            set_question_field(field_name='author', field_value=single_author_name, question_value=question_value,
                               topic_questions=topic_questions, df=questions_for_df)

    df = pd.DataFrame(
        questions_for_df,
        columns=[
            'topic_name', 'question_value', 'question_text', 'answer', 'extra_positives', 'hard_negatives',
            'comment', 'source', 'author', 'tournament', 'date', 'source_url',
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

            if i < len(lines) and not lines[i].startswith('Вопрос'):
                i += 1

    return questions, df
