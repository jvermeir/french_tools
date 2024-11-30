import html
import json
import os.path
import re
from dataclasses import dataclass
from os import listdir
from os.path import isfile, join
from pathlib import Path
from typing import List
import bisect
import matplotlib.pyplot as plt
import requests

whitespace = re.compile(r"\s+")
multiline_anchor_tag = re.compile(r"<a.*?\n*.*?</a>", re.MULTILINE)


@dataclass
class Article:
    file_name: str
    text: str
    sequence_number: int
    word_count: dict[str, int]

    @classmethod
    def from_json(cls, json_data):
        return cls(json_data["file_name"], json_data["text"], json_data["sequence_number"], json_data["word_count"])

    def __init__(self, file_name, text, sequence_number=None, word_count=None):
        self.file_name = file_name
        self.text = text
        self.sequence_number = self.calc_sequence_number(file_name, sequence_number)
        self.word_count: dict[str, int] = self.calc_word_count(word_count, text)

    def __lt__(self, other):
        return self.sequence_number < other.sequence_number

    @staticmethod
    def calc_word_count(word_count: dict[str, int], text):
        if word_count is None:
            return process_file_data(text)
        else:
            return word_count

    @staticmethod
    def calc_sequence_number(file_name, sequence_number):
        if sequence_number is None:
            return get_sequence_number_from_url_or_file(file_name)
        else:
            return sequence_number


def read_data_from_file(path):
    with open(path, 'r', encoding="utf-8") as file:
        return file.read()


def load_userdata():
    with open(Path(__file__).parent / 'secrets' / 'userdata.txt', encoding="utf-8") as file:
        return file.read()


def load_text_from_url(url, data_path):
    print(f'loading {url}')
    userdata = load_userdata()
    cookies = {'wordpress_logged_in_432eefc90b98f2ff74b213258c58921e': userdata}
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, cookies=cookies, headers=headers)
    webpage = response.text

    return webpage


def load_text_from_file(json_file, data_path):
    print(f'loading {json_file} from {data_path}')
    with open(data_path / json_file, "r", encoding="utf-8") as f:
        data: Article = Article(**json.loads(f.read()))

    return data.text


def remove_junk_words(word):
    if re.match('^[0-9]+[€%]+$', word) or re.match('^[0-9]+$', word) or re.match('^\*\*\*$', word):
        return ''
    return word.strip()


def unescape(data):
    return html.unescape(data)


def split_words(text):
    words = [remove_junk_words(word) for word in text.lower().split(' ')]
    return list(filter(lambda w: len(w.strip()) > 0, words))


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
    result = unescape(data)
    result = result.replace('</li>', ' ').replace('</i>', ' ').replace('<i>', ' ').replace('<br/>', ' ').replace(
        '<br />', ' ').replace('<br>', ' ').replace('<p>', ' ').replace('</p>', ' ').replace('</span>', ' ').replace(
        '</strong>', ' ').replace('“','')
    result = re.sub('<strong.*?>', ' ', result)
    result = re.sub('<span.*?>', ' ', result)
    result = multiline_anchor_tag.sub(' ', result, re.MULTILINE)
    result = re.sub('\\[.*?]', '', result)
    result = result.replace('\n', ' ').replace('.', ' ').replace(',', ' ').replace(':', ' ').replace('\'', '').replace(
        '(', ' ').replace(')', ' ').replace('?', ' ').replace('!', ' ').replace('!', ' ').replace('$', ' ').replace('%',
                                                                                                                    ' ')

    return whitespace.sub(' ', result).strip()


def extract_text_from_all_p_sections(p_sections):
    return [extract_text_from_p_section(text) for text in p_sections]


def process_file_data(text_from_file):
    sections = extract_sections(text_from_file)
    transcription_section = extract_transcription_section(sections)
    p_sections = extract_p_sections(transcription_section)
    all_text = extract_text_from_all_p_sections(p_sections)

    return group_words_in_list(all_text)


def write_article(article: Article, data_path: Path):
    filename = construct_article_data_file_name(article.sequence_number, data_path)
    with open(Path(__file__).parent / filename, 'w') as file:
        file.write(json.dumps(article.__dict__))
    print(f'write {filename} with {len(article.word_count.keys())} words')


def construct_article_data_file_name(sequence_number, data_path: Path) -> Path:
    file_name = str(sequence_number) + '.json'
    return data_path / file_name


def load_file_list(urls_data_file, data_path: Path):
    with open(data_path / urls_data_file, 'r', encoding="utf-8") as file:
        urls = file.readlines()

    return urls


def get_sequence_number_from_url_or_file(url):
    file_name = url.strip('/').split('/')[-1]
    sequence_number = file_name.split('-')[0]
    if sequence_number.endswith('.json'):
        sequence_number = sequence_number[:-5]

    return int(float(sequence_number))


def get_new_article(data_loader_func, url, data_path: Path, reload=False):
    article_path = data_path / 'articles'
    article_file_name = construct_article_data_file_name(get_sequence_number_from_url_or_file(url), article_path)
    if not os.path.exists(article_file_name) or reload:
        return Article(url, data_loader_func(url, article_path))
    else:
        print(f'skipping {article_file_name}')
        return None


def sum_counts(articles):
    counts = dict()
    for article in articles:
        for word in article.word_count.keys():
            if word in counts:
                counts[word] = counts[word] + article.word_count[word]
            else:
                counts[word] = 1

    return counts


def sync_podcasts(urls_data_file, data_root: Path, data_loader_func=load_text_from_url) -> int:
    data_path = Path(__file__).parent / data_root
    urls = load_file_list(urls_data_file, data_path)
    urls = [url.strip() for url in urls]
    data = [get_new_article(data_loader_func, url, data_path) for url in urls]
    data = [article for article in data if article is not None]
    for article in data:
        write_article(article, data_path / 'articles')

    return len(data)


def is_word_in_list(word, words: dict):
    return word in words


def word_occurs_first_in(word, articles: List[Article]):
    filtered_list: List[Article] = sorted(
        list(filter(lambda article: is_word_in_list(word, article.word_count), articles)))

    return filtered_list[0].sequence_number


@dataclass
class WordCount:
    def __init__(self, episode: int, count: int, words: List[str]):
        self.episode = episode
        self.count = count
        self.words = words

    def __eq__(self, other):
        return self.episode == other.episode and self.count == other.count and self.words == other.words

    def __str__(self):
        return f'episode:{self.episode},count:{self.count},word:[{self.words}]'

    def __lt__(self, other):
        return self.episode < other.episode

    @classmethod
    def from_dict(cls, data):
        return cls(data['episode'], data['count'], data['words'])


class WordCountJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, WordCount):
            return {
                'episode': obj.episode,
                'count': obj.count,
                'words': obj.words
            }
        return super().default(obj)


def word_count_to_json(word_count: List[WordCount]):
    return json.dumps([word.__dict__ for word in word_count])


def analyze_articles(articles: List[Article]) -> list[WordCount]:
    first_occurrences = dict()

    words = set()
    [words.update(list(article.word_count.keys())) for article in articles]

    for word in words:
        first_occurrence = word_occurs_first_in(word, articles)
        word_list = first_occurrences.get(first_occurrence, [])
        bisect.insort(word_list, word)
        first_occurrences[first_occurrence] = word_list

    result = []
    [result.append(WordCount(file, len(first_occurrences[file]),(first_occurrences[file]))) for file in first_occurrences.keys()]
    return result


def analyze(data_path: Path):
    articles_path = data_path / 'articles'
    data_files = [f for f in listdir(articles_path) if isfile(join(articles_path, f)) and f.endswith('.json')]

    articles = list[Article]()
    for data_file in data_files:
        with open(articles_path / data_file, 'r') as file:
            article: Article = Article(**json.load(file))
            articles.append(article)

    first_occurrences = analyze_articles(articles)

    first_occurances_file = data_path / 'first_occurrences.json'
    with open(first_occurances_file, 'w') as file:
        file.write(json.dumps(first_occurrences, cls=WordCountJSONEncoder))
        print(f'output in {str(first_occurances_file)}')


def re_load(data_path: Path):
    article_folder = Path(__file__).parent / data_path / 'articles'
    data_files = [f for f in listdir(article_folder) if isfile(join(article_folder, f)) and f.endswith('.json')]

    data_loader_func = load_text_from_file
    articles = [get_new_article(data_loader_func, file, data_path, True) for file in data_files]
    articles = [article for article in articles if article is not None]

    for article in articles:
        write_article(article, article_folder)

    return articles


def plot_word_counts(data_path:Path, output_file):
    with open(data_path / 'first_occurrences.json', "r", encoding="utf-8") as f:
        word_counts = [WordCount.from_dict(item) for item in json.load(f)]
    word_counts.sort()
    episodes = [wc.episode for wc in word_counts]
    word_lengths = [len(wc.words) for wc in word_counts]
    total_number_of_words = sum(word_count.count for word_count in word_counts)

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(episodes, word_lengths, color='skyblue')

    for bar, word_length in zip(bars, word_lengths):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, height / 2, str(word_length), ha='center', va='center', fontsize=8, rotation=90)

    ax.set_xlabel('Episode')
    ax.set_ylabel('Number of Words')
    ax.set_title('Number of new Words per Episode, Total: ' + str(total_number_of_words))
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()
    print(f'output in {output_file}')
