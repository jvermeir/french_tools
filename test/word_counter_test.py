from word_counter import split_words, group_words, Article, group_words_per_article, extract_transcription_section, \
    extract_sections, extract_p_sections, extract_text_from_p_section, extract_text_from_all_p_sections, \
    group_words_in_list
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
    TestCase().assertEquals(words, {'bonjour': 1, 'podcast': 3, 'épisode': 1})


def test_group_words():
    words = group_words(split_words('vous…[00:00:12] Salut à tous [King Krule – Lonely Blue] double double'))
    TestCase().assertDictEqual({'vous…': 1, 'salut': 1, 'à': 1, 'tous': 1, 'double': 2}, words)


def test_list_of_articles():
    article1 = Article(file_name='file1', text='woord1 woord2')
    article2 = Article(file_name='file2', text='woord2, woord3')
    article3 = Article(file_name='file3', text='woord4')

    articles = group_words_per_article(
        {article1.file_name: article1, article2.file_name: article2, article3.file_name: article3})

    TestCase().assertDictEqual(
        {'file1': Article(file_name='file1', text='woord1 woord2', word_count={'woord1': 1, 'woord2': 1}),
         'file2': Article(file_name='file2', text='woord2, woord3', word_count={'woord2': 1, 'woord3': 1}),
         'file3': Article(file_name='file3', text='woord4', word_count={'woord4': 1})},
        articles
    )
    TestCase().assertEquals(article1.word_count, dict())


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
    TestCase().assertEquals(extracted_data, expected_data)


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
            </p>"""
        , """<p>
            épisode du Cottongue Podcast.
        </p>"""
    ]
    TestCase().assertEquals(extracted_data, expected_data)


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
    TestCase().assertEquals(plain_text, expected_data)


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
    TestCase().assertEquals(extracted_data, expected_data)

