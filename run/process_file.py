import textract
from docx import Document
import re
from string import ascii_uppercase
from flair.data import Sentence
import dash_html_components as html
import run.tokenization as tkz


def load_text(doc_path):
    return textract.process(doc_path, encoding='utf-8').decode("utf8").replace("|", "\t")


def flair_predict_tags(text, tagger):
    """ Predict using flair tagger"""
    sentence = Sentence(text)
    tagger.predict(sentence)
    return sentence


def build_pseudonymisation_map_flair(sentences, pseudos, acceptance_score, tags="all"):
    """
    Gets all replacements to be made in pseudonimized text using flair tagged sentences

    :param sentences: list of tuples (flair tagged sentences, original)
    :param pseudos: list of pseudos to be used
    :param acceptance_score: minimum confidence score to accept NER tag
    :return: dict: keys are spans in sentence, values are pseudos
    """

    replacements = {}
    mapping = {}
    for sentence in sentences:
        for entity in sentence[0].get_spans('ner'):
            if entity.score > acceptance_score and entity.tag != '0' and (entity.tag in tags or tags == "all"):
                # ajouter le score en param

                # TODO refaire la gestion des B et I tags
                for token in entity.tokens:
                    if token.text.lower() not in mapping:
                        mapping[token.text.lower()] = pseudos.pop(0)

                    replacements[sentence[1][token.idx - 1]] = mapping[token.text.lower()]

    return replacements


def pseudonymize_text(replacements, text):
    """ Create new text with pseudos in place of NER """
    index = 0
    pseudonymized_text = ''
    for key in sorted(replacements.keys()):
        chunk = text[index:key[0]]
        # print(text[key[0]:key[1]])
        pseudonymized_text += chunk
        pseudonymized_text += replacements[key]
        index = key[1]

    pseudonymized_text += text[index:]

    return pseudonymized_text


def pseudonymize_html_text(replacements, text):
    """ Create html blocs with pseudos in place of NER for dash tool"""

    index = 0
    pseudonymized_text = ''
    for key in sorted(replacements.keys()):
        chunk = text[index:key[0]]
        # print(text[key[0]:key[1]])
        pseudonymized_text += chunk
        pseudonymized_text += "<ano>" + replacements[key] + "</ano>"
        index = key[1]

    pseudonymized_text += text[index:]

    return pseudonymized_text


def write_docx_file(text, path):
    """Write pseudonimized file to docx"""
    document = Document()
    paragraph = document.add_paragraph(text)
    document.save(path)


def create_html_file(text, sent_tokenizer, word_tokenizer, tagger, acceptance_score=0.5):
    """ Create HMTL files for the Dash tool """
    pseudos = ["{}...".format(letter) for letter in ascii_uppercase]

    sentences = tkz.tokenize_text(text, sent_tokenizer, word_tokenizer)

    tagged_sentences = []
    for sentence in sentences:
        pseudo_sentence = " ".join([text[word[0]: word[1]] for word in sentence])
        tagged_sentence = flair_predict_tags(pseudo_sentence, tagger)
        tagged_sentences.append((tagged_sentence, sentence))

    replacements = build_pseudonymisation_map_flair(tagged_sentences, pseudos, acceptance_score)
    pseudonymized_text = pseudonymize_html_text(replacements, text)

    html_text = []

    for p in pseudonymized_text.split("\n"):
        html_text.append(highlight_pseudo(p))

    return html_text


def highlight_pseudo(paragraph):
    """ Hghlight pseudonymized text for Dash tool """
    index = 0

    new_str = []
    for change in re.finditer('<ano>(.*?)</ano>', paragraph):
        b = change.start(0)
        e = change.end(0)
        new_str.append(paragraph[index:b])
        new_str.append(html.Mark(change.group(1), style={'color': 'blue'}))
        index = e

    new_str.append(paragraph[index:])

    return html.P(new_str)


def create_CoNLL(tagged_sentences, path):
    """ Write CoNLL file """
    with open(path, "w") as file:
        for sent in tagged_sentences:
            for token in sent[0]:
                file.write(f"{token.text}\t{token.get_tag('ner').value}\n")


def process_file(path, sent_tokenizer, word_tokenizer, tagger, acceptance_score=0.5, docx_path=False, CoNLL_path=False, tags="all"):
    """
    Pseudonymization of text file. Can create CoNLL file, HTML of docx. Only NLTK tokenizer supported for the moment
    :param acceptance_score: minimum confidence score to accept ner tagging
    :param tagger: A NER tagger
    :param path: original file path
    :param sent_tokenizer: Sentence tokenizer
    :param word_tokenizer: Word tokenizer
    :param docx_path: If path is given will write DOCX file
    :param CoNLL_path: If path is given will write CoNLL file
    :return: Pseudonymized text
    """

    text = load_text(path)
    pseudos = ["{}...".format(letter) for letter in ascii_uppercase]

    sentences = tkz.tokenize_text(text, sent_tokenizer, word_tokenizer)

    tagged_sentences = []
    for sentence in sentences:
        pseudo_sentence = " ".join([text[word[0]: word[1]] for word in sentence])
        tagged_sentence = flair_predict_tags(pseudo_sentence, tagger)
        tagged_sentences.append((tagged_sentence, sentence))

    if CoNLL_path:
        create_CoNLL(tagged_sentences, CoNLL_path)

    replacements = build_pseudonymisation_map_flair(tagged_sentences, pseudos, acceptance_score, tags)
    pseudonymized_text = pseudonymize_text(replacements, text)

    if docx_path:
        write_docx_file(pseudonymized_text, docx_path)

    return pseudonymized_text


if __name__ == '__main__':
    from nltk.tokenize import WordPunctTokenizer, PunktSentenceTokenizer
    from flair.models import SequenceTagger

    word_tokenizer = WordPunctTokenizer()
    tagger = SequenceTagger.load('fr-ner')
    sent_tokenizer = PunktSentenceTokenizer("nltk_data/tokenizers/punkt/french.pickle")
    path = "path_to_doc"
    word_tokenizer = WordPunctTokenizer()
    process_file(path, sent_tokenizer, word_tokenizer, tagger, docx_path=False, CoNLL_path=False, tags=["PER"])
