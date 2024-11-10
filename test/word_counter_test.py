import json
import os
from pathlib import Path

from word_counter import split_words, group_words, Article, extract_transcription_section, \
    extract_sections, extract_p_sections, extract_text_from_p_section, extract_text_from_all_p_sections, \
    group_words_in_list, sync_podcasts, get_sequence_number_from_file, process_file_data
from unittest import TestCase


def test_split_words():
    words = split_words('vous…[00:00:12] Salut à tous [King Krule – Lonely Blue] bam')
    TestCase().assertListEqual(['vous…', 'salut', 'à', 'tous', 'bam'], words)


def test_group_words_in_list():
    data = [
        """Bonjour Podcast. Podcast""",
        """épisode Podcast."""
    ]
    words = group_words_in_list(data)
    TestCase().assertEqual(words, {'bonjour': 1, 'podcast': 3, 'épisode': 1})


def test_group_words():
    words = group_words(split_words('vous…[00:00:12] Salut à tous [King Krule – Lonely Blue] double double'))
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
                    <strong>troisième</strong>
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
            épisode du Cottongue Podcast.
        </p>"""

    plain_text = extract_text_from_p_section(data)
    expected_data = """Bonjour à tous et bienvenue ! C’est le troisième épisode du Cottongue Podcast."""
    TestCase().assertEqual(plain_text, expected_data)


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
        """Bonjour à tous et bienvenue ! C’est le troisième épisode du Cottongue Podcast."""
        , """épisode du Cottongue Podcast."""
    ]
    TestCase().assertEqual(extracted_data, expected_data)


def load_page_from_test_data(json_file):
    filename = "./test_files/" + json_file
    with open(Path(__file__).parent / filename, "r") as f:
        data:Article = json.load(f)

    return data['text']


def test_list_of_episodes_is_loaded():
    os.makedirs('./test/test_files/output', exist_ok=True)
    extracted_data:list[Article] = sync_podcasts('urls.txt', './test/test_files/', load_page_from_test_data)
    TestCase().assertEqual(2, len(extracted_data))
    episode_1 = extracted_data[0]
    episode_2 = extracted_data[1]
    TestCase().assertEqual('x/1-test.json', episode_1.file_name)
    TestCase().assertEqual('x/2-test.json', episode_2.file_name)
    TestCase().assertEqual(1, episode_1.sequence_number)
    TestCase().assertEqual(2, episode_2.sequence_number)

    TestCase().assertTrue(episode_1.text.index('href="https://innerfrench.com/01-learn-french-naturally/"')>0)
    TestCase().assertTrue(episode_2.text.index('href="https://innerfrench.com/02-vivre-avec-robots/feed/"')>0)

    TestCase().assertEqual(399, len(episode_1.word_count.keys()))
    TestCase().assertEqual(398, len(episode_2.word_count.keys()))


def test_get_sequence_number_from_file():
    TestCase().assertEqual(2, get_sequence_number_from_file('https://innerfrench.com/02-vivre-avec-robots/'))
