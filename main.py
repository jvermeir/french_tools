from pathlib import Path
import argparse
from word_counter import read_data_from_file, extract_sections, extract_transcription_section, extract_p_sections, \
    extract_text_from_all_p_sections, group_words_in_list, sync_podcasts, analyze, re_load
from word_exercise import do_exercise

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(help='help for subcommand', dest="subcommand", required=True)

sync_data_parser = subparsers.add_parser('sync', help='sync data from Inner French website and store on filesystem')
analyze_data_parser = subparsers.add_parser('analyze', help='analyze data from Inner French website')
re_analyze_parser = subparsers.add_parser('reload', help='reanalyze data using files downloaded from Inner French website')
exercise_parser = subparsers.add_parser('exercise', help='train words from taaltempo')
exercise_parser.add_argument('--file',
                              dest='file_name',
                              type=str,
                              help='The name of the file to load from data/words',
                              )

command = parser.parse_args()

if command.subcommand == 'sync':
    sync_podcasts('urls.txt', Path('data'))
elif command.subcommand == 'analyze':
    analyze(Path('data'))
elif command.subcommand == 'reload':
    re_load(Path('data'))
elif command.subcommand == 'exercise':
    do_exercise(command.file_name)
else:
    print(f'unknown command {command.subcommand}')


# stuff to experiment with

def load_a_test_file():
    test_file = Path(__file__).parent / 'test' / 'test_files' / '04-theorie-genre'
    text = read_data_from_file(test_file)
    sections = extract_sections(text)
    transcription_section = extract_transcription_section(sections)
    p_sections = extract_p_sections(transcription_section)
    all_text = extract_text_from_all_p_sections(p_sections)
    words = (group_words_in_list(all_text))
    print(words)

# uncomment to test basic functionality
# load_a_test_file()