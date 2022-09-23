# YoGa - Multilingual Question Answering Project

Seminar project by Tsimafei Prakapenka under supervision of S. Osterman.<br>
The main goal of this project is to build a system to answer Jeopardy-like questions in Russian.


## High-level tasks:

### Main sub-tasks

### How to start
First, install required packages by this command:

`pip install -r requirements.txt`

### How to train model

`bash allen_train.sh 1 16 0.0001 42 'data/question_to_answer/yoga_' configs/mT5.jsonnet`
`bash allen_train.sh 1 16 0.0001 42 'data/topic_and_question_to_answer/yoga_' configs/mT5.jsonnet`

### Repository Structure
    - data - YoGa QA source and processed data
    - src - source Python code for file preprocessing
    - config - configuration file
