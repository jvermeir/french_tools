from pathlib import Path
import argparse
from word_counter import read_data_from_file, extract_sections, extract_transcription_section, extract_p_sections, \
    extract_text_from_all_p_sections, group_words_in_list, sync_podcasts

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(help='help for subcommand', dest="subcommand", required=True)

sync_data_parser = subparsers.add_parser('sync', help='sync data from Inner French website and store on filesystem')
analyze_data_parser = subparsers.add_parser('analyze', help='analyze data from Inner French website')

command = parser.parse_args()

if command.subcommand == 'sync':
    sync_podcasts('urls.txt', './data/')
elif command.subcommand == 'analyze':
    print('todo')
else:
    print(f'unknown command {command.subcommand}')


# stuff to experiment with

def load_a_test_file():
    test_file = Path(__file__).parent / "./test/test_files/04-theorie-genre"
    text = read_data_from_file(test_file)
    sections = extract_sections(text)
    transcription_section = extract_transcription_section(sections)
    p_sections = extract_p_sections(transcription_section)
    all_text = extract_text_from_all_p_sections(p_sections)
    words = (group_words_in_list(all_text))
    print(words)

# uncomment to test basic functionality
# load_a_test_file()