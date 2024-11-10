from pathlib import Path

from word_counter import read_data_from_file, extract_sections, extract_transcription_section, extract_p_sections, \
    extract_text_from_all_p_sections, group_words_in_list, sync_podcasts

sync_podcasts('urls.txt', './data/')


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