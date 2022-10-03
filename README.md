# YoGa-QA - Multilingual Question Answering Project

The main goal of this project is to build a system to answer Jeopardy-like questions in Russian.
This work is conducted under supervision of [Simon Ostermann](https://scholar.google.com/citations?user=kOHpHZsAAAAJ&hl=en).<br>

At the moment, there are two main contributions of this repository:
- [Jeopardy-like QA dataset in Russian](data/yoga_questions.csv). 
  This is a new, independently collected edition of dataset, introduced by [Mikhalkova (2021)](https://arxiv.org/pdf/2112.02325.pdf).
- [mT5-based neural model to solve this task](https://drive.google.com/file/d/1myF_TdIraDz5DJHzVNvr2j345NU7OSpi/view?usp=sharing)
    Please, be aware that current quality of the model is low: 2/2560 answers on test set. I am researching various ways to improve the system.

For more detailed description, please, read [intermediate seminar report](meta/Prakapenka_BERT_seminar_report.pdf).

## Repository Structure
    - data - YoGa-QA source data and parsed dataset
    - meta - project reports + helper instructions (e.g. how to connect to GPU servers)
    - src/scraper - Python code for data scraping and parsing
    - src/models - Python code for training neural models (AllenNLP)

## Data Collection
‘Svoya Igra’ (Own Game) is a Russian analogue of Jeopardy. There is a TV version of this game, running from 1994. Additionally, there is a big community of enthusiasts in Russian-speaking countries, who write their owns questions and run championships. There is an official web database of the questions, written by professional authors - https://db.chgk.info/. There is a inital version Own Game dataset, introduced by [Mikhalkova (2021)](https://arxiv.org/pdf/2112.02325.pdf).

To note, Your Game is less accurate translation for 'Svoya Igra' than Own Game, but I like the Yoga abbreviation ;)

#### Licence
The data was scraped from [the questions database](https://db.chgk.info/tour/SVOYAK) and protected by [the copyright (in Russian)](https://db.chgk.info/copyright), with underlying licences included:
- [CC BY-ND 4.0](https://creativecommons.org/licenses/by-nd/4.0/)
- [BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode)
- [CC BY-NC-ND 4.0](https://creativecommons.org/licenses/by-nc-nd/4.0/)

#### Database Schema
***Required fields***: topic_name, question_value, question_text, answer.
***Optional fields***: extra_positives, hard_negatives, comment, source, author, tournament, date, source_url.

#### Sample Entry
| topic_name  | question_value | question_text  | answer
| ----------- | -------------  | ----------  |  ---------
| *Океаны*    | *4*              |*Океан, в отличие от своих братьев, не участвовал В НЕЙ, благодаря чему сохранил свое положение, а не был низвергнут в Тартар.*| *титаномахия*
| *Oceans*      | *4*              |*The ocean, unlike its brothers, did not participate in IT, thanks to which it retained its position, and was not thrown into Tartarus.*| *Titanomachy*

| extra_positives         | hard_negatives | comment  | source
| -----------             | -------------  | ----------  |  ---------
| *битва титанов и богов*  | *гигантомахия* | - | https://ru.wikipedia.org/wiki/Океан_(мифология)
| *Battle of titans and gods*     | *Gigantomachy*              | - | *English analogue:* https://en.wikipedia.org/wiki/Oceanus

| <div style="width:100px">author</div>         | tournament | <div style="width:90px">date</div> | <div style="width:90px">source_url</div> |
| -----------             | -------------  | ----------  |  ---------
| *Иделия Айзятулова, Андрей Мартыненко, Александр Рождествин*  | *XII Кубок Европы по интеллектуальным играм среди студентов (Витебск). Своя игра* | *2016-10-28* | https://db.chgk.info/txt/eu16stsv.txt |
| *Ideliya Aizyatulova, Andrey Martynenko, Alexander Rozhdestvin*      | *XII European Student Intellectual Games Cup (Vitebsk). Own game*              | *2016-10-28* |  https://db.chgk.info/txt/eu16stsv.txt |


## Models

#### How to start
First, install required packages by this command:
`pip install -r model_requirements.txt`
Then, set current working directory to the `src/models` and run all the following commands:
`cd src/models`

#### How to train model
`bash allen_train.sh GPU_ID BATCH_SIZE LEARNING_RATE SEED DATA_FOLDER CONFIG_NAME`

For example:
`bash allen_train.sh 1 16 0.0001 42 'question_to_answer' configs/mT5.jsonnet`
`bash allen_train.sh 1 8 0.0001 42 'topic_and_question_to_answer' configs/mT5.jsonnet`

#### How to make predictions with trained model
`bash predict.sh PATH_TO_MODEL INPUT_JSONL_PATH OUTPUT_PATH`

For example:
`bash predict.sh archive/mt5_0.0001_batch16_accum8_seed424242/model.tar.gz data/question_to_answer/yoga_test.jsonl predictions/question_to_answer/full_yoga_test_predictions.txt`

-----
Author: _Tsimafei Prakapenka_
