

class YogaQuestion:
    def __init__(self, topic: str, question_value: int, tournament: str, date: str, source_url: str):
        """
        - ID
        - Topic
        - QuestionValue
        - Question
        - Answer
        - Optional. AcceptedAnswers
        - Optional. Author
        - Optional. Source
        - Optional. Link
        - Optional. Tournament
        - Optional. EstimatedComplexity - from 1 to 3.
        - Optional. Year
        """
        self.question_value = question_value
        self.topic = topic
        self.tournament = tournament
        self.date = date
        self.source_url = source_url
        #self.question_text = question_text
        # self.answer = answer
        # self.question_value = question_value
        # self.topic = topic
        # self.author = author
        # self.source =
        pass
