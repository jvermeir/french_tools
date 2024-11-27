from dataclasses import dataclass
from pathlib import Path


@dataclass
class Word:
    question: str
    answer: str

    def __init__(self, question, answer):
        self.question = question
        self.answer = answer


def load_exercise_file(path_to_word_file: Path):
    def get_word_from_line(line):
        if line.find('question')>=0 or line.find("--")>=0:
            return None
        words = line.split('|')
        if words[2].find('//')>0:
            words[2] = words[2].split('//')[0]
        return Word(words[1].strip(), words[2].strip())

    with open(path_to_word_file) as file:
        lines = file.readlines()

    words = [get_word_from_line(line) for line in lines]
    return list(filter(lambda word: word is not None, words))


def do_exercise(file_name):
    correct = 0
    incorrect = 0
    words = load_exercise_file(file_name)
    for word in words:
        answer = input(word.question + ': ').strip()
        if word.answer == answer:
            print("check")
            correct += 1
        else:
            print(f"Incorrect answer: {word.answer}")
            incorrect += 1
    print(f"Correct: {correct}, Incorrect: {incorrect}")