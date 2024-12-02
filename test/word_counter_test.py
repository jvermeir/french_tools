import json
import os
import shutil
from pathlib import Path
from unittest import TestCase

from word_counter import split_words, group_words, Article, extract_transcription_section, \
    extract_sections, extract_p_sections, extract_text_from_p_section, extract_text_from_all_p_sections, \
    group_words_in_list, sync_podcasts, get_sequence_number_from_url_or_file, process_file_data, sum_counts, \
    word_occurs_first_in, analyze_articles, remove_junk_words, unescape, \
    WordCount


def test_remove_junk():
    TestCase().assertEqual('', remove_junk_words('140'))
    TestCase().assertEqual('', remove_junk_words('1500\u20ac'))
    TestCase().assertEqual('', remove_junk_words('100%'))
    TestCase().assertEqual('', remove_junk_words('***'))
    TestCase().assertEqual('', remove_junk_words(','))
    TestCase().assertEqual('', remove_junk_words('-'))
    TestCase().assertEqual('abcdé', remove_junk_words('abcdé'))


def test_split_words():
    words = split_words('vous… Salut à tous bam')
    TestCase().assertListEqual(['vous…', 'salut', 'à', 'tous', 'bam'], words)


def test_group_words_in_list():
    data = [
        """Bonjour Podcast Podcast""",
        """épisode Podcast"""
    ]
    words = group_words_in_list(data)
    TestCase().assertEqual(words, {'bonjour': 1, 'podcast': 3, 'épisode': 1})


def test_group_words():
    words = group_words(split_words('vous… Salut à tous double double'))
    TestCase().assertDictEqual({'vous…': 1, 'salut': 1, 'à': 1, 'tous': 1, 'double': 2}, words)


def test_process_file():
    data = """
        <!doctype html>
    <html lang="fr-FR">
          <section class="elementor-section type="section">
          </section>
      <section class="elementor-section elementor-top-section elementor-element elementor-element-5f957d29 elementor-section-boxed elementor-section-height-default elementor-section-height-default" data-id="5f957d29" data-element_type="section">
          <h2 class="elementor-heading-title elementor-size-default">Transcription de l'épisode</h2>
            <p>
                Bonjour 
                <span class="tooltips " style="" title="third">
                    <strong style="color: var( --e-global-color-text );">troisième</strong>
                </span>
                épisode
            </p>
      </section>
    bla bla
        """
    TestCase().assertEqual(process_file_data(data), {'bonjour': 1, 'troisième': 1, 'épisode': 1})


def test_extract_sections():
    data = """
        <!doctype html>
    <html lang="fr-FR">
      <section class="elementor-section type="section">
      </section>
      <section class="elementor-section  _type="section">
      </section>
      test
    """
    sections = extract_sections(data)
    TestCase().assertListEqual(
        sections,
        [
            """<section class="elementor-section type="section">
      </section>""",
            """<section class="elementor-section  _type="section">
      </section>"""
        ]
    )


def test_extract_transcription_section():
    data = """
    <!doctype html>
<html lang="fr-FR">
      <section class="elementor-section type="section">
      </section>
  <section class="elementor-section elementor-top-section elementor-element elementor-element-5f957d29 elementor-section-boxed elementor-section-height-default elementor-section-height-default" data-id="5f957d29" data-element_type="section">
      <h2 class="elementor-heading-title elementor-size-default">Transcription de l'épisode</h2>
        <p>
            Bonjour à tous et bienvenue ! C’est le
            <span class="tooltips " style="" title="third">
                <strong>troisième</strong>
            </span>
            épisode du Cottongue Podcast.
        </p>
  </section>
bla bla
    """
    extracted_data = extract_transcription_section(extract_sections(data))
    expected_data = """<section class="elementor-section elementor-top-section elementor-element elementor-element-5f957d29 elementor-section-boxed elementor-section-height-default elementor-section-height-default" data-id="5f957d29" data-element_type="section">
      <h2 class="elementor-heading-title elementor-size-default">Transcription de l'épisode</h2>
        <p>
            Bonjour à tous et bienvenue ! C’est le
            <span class="tooltips " style="" title="third">
                <strong>troisième</strong>
            </span>
            épisode du Cottongue Podcast.
        </p>
  </section>"""
    TestCase().assertEqual(extracted_data, expected_data)


def test_extract_p_sections():
    data = """
    <!doctype html>
<html lang="fr-FR">
      <section class="elementor-section type="section">
      </section>
  <section class="elementor-section elementor-top-section elementor-element elementor-element-5f957d29 elementor-section-boxed elementor-section-height-default elementor-section-height-default" data-id="5f957d29" data-element_type="section">
      <h2 class="elementor-heading-title elementor-size-default">Transcription de l'épisode</h2>
        <p>
            Bonjour à tous et bienvenue ! C’est le
            <span class="tooltips " style="" title="third">
                <strong>troisième</strong>
            </span>
            épisode du Cottongue Podcast.
        </p>
        <p>
            épisode du Cottongue Podcast.
        </p>
  </section>
bla bla
    """
    section = extract_transcription_section(extract_sections(data))
    extracted_data = extract_p_sections(section)
    expected_data = [
        """<p>
            Bonjour à tous et bienvenue ! C’est le
            <span class="tooltips " style="" title="third">
                <strong>troisième</strong>
            </span>
            épisode du Cottongue Podcast.
        </p>""",
        """<p>\n            épisode du Cottongue Podcast.\n        </p>"""
    ]
    TestCase().assertEqual(extracted_data, expected_data)


def test_extract_text_from_p_section():
    data = """<p>
    <br/>
    <a id="sonaar_ts-6726738dd4736" :'' }) ;">[00:00:10]</a>
            Bonjour à tous et bienvenue ! C’est le
            <span class="tooltips " style="" title="third">
                <strong>troisième</strong>
            </span>
            <strong junk>
            épisode du Cottongue Podcast.
            </strong>
            ? ! %
            [00:00:12] 
            [King Krule – Lonely Blue]
            <i></i></li> 
            “
        </p>"""

    plain_text = extract_text_from_p_section(data)
    expected_data = """Bonjour à tous et bienvenue C’est le troisième épisode du Cottongue Podcast"""
    TestCase().assertEqual(expected_data, plain_text)


def test_extract_text_from_all_p_sections():
    data = """
        <!doctype html>
    <html lang="fr-FR">
          <section class="elementor-section type="section">
          </section>
      <section class="elementor-section elementor-top-section elementor-element elementor-element-5f957d29 elementor-section-boxed elementor-section-height-default elementor-section-height-default" data-id="5f957d29" data-element_type="section">
          <h2 class="elementor-heading-title elementor-size-default">Transcription de l'épisode</h2>
            <p>
                Bonjour à tous et bienvenue ! C’est le
                <span class="tooltips " style="" title="third">
                    <strong>troisième</strong>
                </span>
                épisode du Cottongue Podcast.
            </p>
            <p>
                épisode du Cottongue Podcast.
            </p>
      </section>
    bla bla
    """
    section = extract_transcription_section(extract_sections(data))
    extracted_data = extract_text_from_all_p_sections(extract_p_sections(section))
    expected_data = [
        """Bonjour à tous et bienvenue C’est le troisième épisode du Cottongue Podcast"""
        , """épisode du Cottongue Podcast"""
    ]
    TestCase().assertEqual(extracted_data, expected_data)


def load_page_from_test_data(json_file, data_path: Path):
    data_file = data_path / json_file
    with open(data_file, "r") as f:
        data = Article(**json.loads(f.read()))

    return data.text


# TODO: test to check if data is loaded from a real file

def test_podcasts_are_synced(tmpdir):
    TestCase().assertFalse(os.path.exists(tmpdir / 'articles' / '2.json'))

    shutil.copy(Path(__file__).parent / 'test_files' / 'urls.txt', tmpdir)
    os.makedirs(tmpdir / 'articles' / 'x')
    shutil.copy(Path(__file__).parent / 'test_files' / '1.json', tmpdir / 'articles')
    shutil.copy(Path(__file__).parent / 'test_files' / '2-test.json', tmpdir / 'articles' / 'x')

    TestCase().assertEqual(1, sync_podcasts('urls.txt', tmpdir, load_page_from_test_data))
    TestCase().assertTrue(os.path.exists(tmpdir / 'articles' / '2.json'))


def test_get_sequence_number_from_url():
    TestCase().assertEqual(2, get_sequence_number_from_url_or_file('https://innerfrench.com/02-vivre-avec-robots/'))


def test_get_sequence_number_from_file_name():
    TestCase().assertEqual(2, get_sequence_number_from_url_or_file('2.json'))


def test_word_counts_are_summed_correctly():
    file1 = """
      <section>
          <h2>Transcription de l'épisode</h2>
            <p>
            occursTwice onlyInOne
            </p>
      </section>
    """

    file2 = """
      <section>
          <h2Transcription de l'épisode</h2>
            <p>
            occursTwice onlyInTwo
            </p>
      </section>
    """

    article1 = Article('/x/1', file1)
    article2 = Article('/x/2', file2)

    word_counts = sum_counts([article1, article2])

    TestCase().assertEqual(2, word_counts.get('occurstwice'))
    TestCase().assertEqual(1, word_counts.get('onlyinone'))
    TestCase().assertEqual(1, word_counts.get('onlyintwo'))


def test_word_occurs_first():
    file1 = """
      <section>
          <h2>Transcription de l'épisode</h2>
            <p>
            occursTwice onlyInOne
            </p>
      </section>
    """

    file2 = """
      <section>
          <h2>Transcription de l'épisode</h2>
            <p>
            occursTwice onlyInTwo
            </p>
      </section>
    """

    article1 = Article('/x/1', file1)
    article2 = Article('/x/2', file2)

    word_counts = [article1, article2]

    TestCase().assertEqual(1, word_occurs_first_in('occurstwice', word_counts))
    TestCase().assertEqual(1, word_occurs_first_in('onlyinone', word_counts))
    TestCase().assertEqual(2, word_occurs_first_in('onlyintwo', word_counts))

    TestCase().assertEqual(1, word_occurs_first_in('occurstwice', [article2, article1]))


def test_new_words_report():
    file1 = """
      <section>
          <h2>Transcription de l'épisode</h2>
            <p>
            occursTwice onlyInOne
            </p>
      </section>
    """

    file2 = """
      <section>
          <h2>Transcription de l'épisode</h2>
            <p>
            occursTwice onlyInTwo
            </p>
      </section>
    """

    article1 = Article('/x/1', file1)
    article2 = Article('/x/2', file2)

    word_counts = [article1, article2]

    articles = analyze_articles(word_counts)
    articles.sort()
    TestCase().assertEqual('[{"episode": 1, "count": 2, "words": ["occurstwice", "onlyinone"]}, {"episode": 2, "count": 1, "words": ["onlyintwo"]}]'.strip(), json.dumps([ob.__dict__ for ob in articles]).strip())
    TestCase().assertEqual([WordCount(1,2,['occurstwice', 'onlyinone']), WordCount(2,1,['onlyintwo'])], articles)


def test_html_characters_are_unescaped():
    data = 'l&#8217;imaginez'
    TestCase().assertEqual('l’imaginez', unescape(data))
