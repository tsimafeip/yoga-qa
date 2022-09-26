# YogaQA
!NB: this repository is still under construction. I will update README and reorganise folders once I finish active phase of development.

Trivia-like QA dataset (in Russian) + neural models to solve this task.
For more detailed description, please, read [the project proposal](meta/Prakapenka_YogaQA.pdf).

The data was scraped from [the questions database](https://db.chgk.info/tour/SVOYAK) and protected by [the copyright (in Russian)](https://db.chgk.info/copyright), with underlying licences included:
- [CC BY-ND 4.0](https://creativecommons.org/licenses/by-nd/4.0/)
- [BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode)
- [CC BY-NC-ND 4.0](https://creativecommons.org/licenses/by-nc-nd/4.0/)


## Database Schema
Required fields: topic_name, question_value, question_text, answer.<br>
Optional fields: extra_positives, hard_negatives, comment, source, author, tournament, date, source_url.
