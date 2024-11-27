from pathlib import Path

from unittest import TestCase

from word_exercise import Word, load_exercise_file


def test_load_exercise_file():
    words = load_exercise_file(Path(__file__).parent / 'test_files' /'word_exercise_test.md')
    TestCase().assertEqual(2, len(words))
    TestCase().assertEqual(words[0], Word('vous prenez?*', 'je prends'))
    TestCase().assertEqual(words[1], Word('et lui?', 'il prend'))
