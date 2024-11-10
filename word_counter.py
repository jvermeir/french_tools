import json
import os.path
import re
from dataclasses import dataclass
from pathlib import Path

import requests

whitespace = re.compile(r"\s+")


@dataclass
class Article:
    file_name: str
    text: str
    sequence_number: int
    word_count: dict[str, int]

    def __init__(self, file_name, text):
        self.file_name = file_name
        self.text = text
        self.sequence_number = get_sequence_number_from_file(file_name)
        self.word_count: dict[str, int] = process_file_data(text)


def read_data_from_file(path):
    with open(path, 'r') as file:
        return file.read()


def load_userdata():
    with open(Path(__file__).parent / "./secrets/userdata.txt") as file:
        return file.read()


def load_from_url(url):
    print(f'loading {url}')
    userdata = load_userdata()
    cookies = {'wordpress_logged_in_432eefc90b98f2ff74b213258c58921e':userdata}
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, cookies=cookies, headers=headers)
    webpage = response.text

    return webpage


def split_words(text):
    data = text.replace('\n', ' ').replace('.', ' ').replace(',', ' ').replace(';', ' ').replace(':', ' ').replace('\'', ' ')
    data = re.sub('\\[.*?]', '', data)
    data = whitespace.sub(" ", data).strip()

    return data.lower().split(" ")


def group_words(data):
    words = dict()
    for word in data:
        if word in words:
            words[word] = words[word] + 1
        else:
            words[word] = 1

    return words


def group_words_in_list(data):
    words_per_line = [group_words(split_words(line)) for line in data]
    words = dict()
    for line in words_per_line:
        for word in line:
            if word in words:
                words[word] = words[word] + line[word]
            else:
                words[word] = line[word]

    return words


def extract_sections(data):
    section_start_positions = [_.start() for _ in re.finditer("<section", data)]
    return [data[start:data.find('</section>', start) + 10] for start in section_start_positions]


def extract_transcription_section(sections):
    return next((section for section in sections if section.find("Transcription de") >= 0), "")


def extract_p_sections(section):
    p_section_start_positions = [_.start() for _ in re.finditer("<p", section)]
    return [section[start:section.find('</p>', start) + 4] for start in p_section_start_positions]


def extract_text_from_p_section(data):
    result = data.replace("<br/>", " ").replace("<p>", " ").replace("</p>", " ").replace("</span>", " ").replace("</strong>", " ").replace(
        "<strong>", " ")
    result = re.sub("<span.*>", " ", result)
    result = re.sub("<a.*</a>", " ", result)

    return whitespace.sub(" ", result).strip()


def extract_text_from_all_p_sections(p_sections):
    return [extract_text_from_p_section(text) for text in p_sections]


def process_file_data(text_from_file):
    sections = extract_sections(text_from_file)
    transcription_section = extract_transcription_section(sections)
    p_sections = extract_p_sections(transcription_section)
    all_text = extract_text_from_all_p_sections(p_sections)

    return group_words_in_list(all_text)


def write_article(article: Article, data_path):
    filename = construct_article_data_file_name(article.sequence_number, data_path)
    with open(Path(__file__).parent / filename, 'w') as file:
        file.write(json.dumps(article.__dict__))


def construct_article_data_file_name(sequence_number, data_path):
    return data_path + str(sequence_number) + '.json'


def load_file_list(urls_data_file, data_path):
    with open(Path(__file__).parent / data_path / urls_data_file, 'r') as file:
        urls = file.readlines()

    return urls


def get_sequence_number_from_file(url):
    file_name = url.strip('/').split('/')[-1]
    sequence_number = file_name.split('-')[0]

    return int(float(sequence_number))


def sync_podcasts(urls_data_file, data_path, data_loader_func=load_from_url):
    urls = load_file_list(urls_data_file, data_path)
    urls = [url.strip() for url in urls]
    data = [get_new_article(data_loader_func, url, data_path) for url in urls]
    data = [article for article in data if article is not None]
    for article in data:
        write_article(article, data_path)
    articles = [Article(a.file_name, a.text) for a in data]

    return articles


def get_new_article(data_loader_func, url, data_path):
    article_file_name = construct_article_data_file_name(get_sequence_number_from_file(url), data_path)
    if not os.path.exists(article_file_name):
        return Article(url, data_loader_func(url))
    else:
        print(f'skipping {article_file_name}')
        return None
