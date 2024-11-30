from pathlib import Path
import argparse
from word_counter import read_data_from_file, extract_sections, extract_transcription_section, extract_p_sections, \
    extract_text_from_all_p_sections, group_words_in_list, sync_podcasts, analyze, re_load, plot_word_counts, \
    analyze_articles
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
plot_parser = subparsers.add_parser('plot', help='plot the word counts and output to a file')
plot_parser.add_argument('--file',
                              dest='output_file_name',
                              type=str,
                              help='The name of the output file',
                              )

command = parser.parse_args()

if command.subcommand == 'sync':
    sync_podcasts('urls.txt', Path('data'))
elif command.subcommand == 'analyze':
    analyze(Path('data'))
elif command.subcommand == 'reload':
    re_load(Path('data'))
elif command.subcommand == 'plot':
    plot_word_counts(Path('data'), command.output_file_name)
elif command.subcommand == 'exercise':
    do_exercise(command.file_name)
else:
    print(f'unknown command {command.subcommand}')
