import base64
import copy
import itertools
import subprocess
from string import ascii_uppercase
from typing import Callable, List

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import textract
from flair.data import Token, Span

from flair.models import SequenceTagger
from sacremoses import MosesTokenizer, MosesDetokenizer, MosesPunctNormalizer

word_tokenizer = MosesTokenizer("fr").tokenize
tagger = SequenceTagger.load('/home/pavel/code/pseudo_conseil_etat/models/flair_embeds/1600_200_200/best-model.pt')


class MosesTokenizerSpans(MosesTokenizer):
    def __init__(self, lang="en", custom_nonbreaking_prefixes_file=None):
        MosesTokenizer.__init__(self, lang=lang,
                                custom_nonbreaking_prefixes_file=custom_nonbreaking_prefixes_file)
        self.lang = lang

    def span_tokenize(
            self,
            text,
            aggressive_dash_splits=False,
            escape=True,
            protected_patterns=None,
    ):
        # https://stackoverflow.com/a/35634472
        import re
        detokenizer = MosesDetokenizer(lang=self.lang)
        tokens = self.tokenize(text=text, aggressive_dash_splits=aggressive_dash_splits,
                               return_str=False, escape=escape,
                               protected_patterns=protected_patterns)
        tail = text
        accum = 0
        tokens_spans = []
        for token in tokens:
            detokenized_token = detokenizer.detokenize(tokens=[token],
                                                       return_str=True,
                                                       unescape=escape)
            escaped_token = re.escape(detokenized_token)

            m = re.search(escaped_token, tail)
            tok_start_pos, tok_end_pos = m.span()
            sent_start_pos = accum + tok_start_pos
            sent_end_pos = accum + tok_end_pos
            accum += tok_end_pos
            tail = tail[tok_end_pos:]

            tokens_spans.append((detokenized_token, (sent_start_pos, sent_end_pos)))
        return tokens_spans



def build_moses_tokenizer(tokenizer: MosesTokenizerSpans,
                          normalizer: MosesPunctNormalizer = None) -> Callable[[str], List[Token]]:
    """
    Wrap Spacy model to build a tokenizer for the Sentence class.
    :param model a Spacy V2 model
    :return a tokenizer function to provide to Sentence class constructor
    """
    try:
        from sacremoses import MosesTokenizer
        from sacremoses import MosesPunctNormalizer
    except ImportError:
        raise ImportError(
            "Please install sacremoses or better before using the Spacy tokenizer, otherwise you can use segtok_tokenizer as advanced tokenizer."
        )

    moses_tokenizer: MosesTokenizerSpans = tokenizer
    if normalizer:
        normalizer: MosesPunctNormalizer = normalizer

    def tokenizer(text: str) -> List[Token]:
        if normalizer:
            text = normalizer.normalize(text=text)
        doc = moses_tokenizer.span_tokenize(text=text, escape=False)
        previous_token = None
        tokens: List[Token] = []
        for word, (start_pos, end_pos) in doc:
            word: str = word
            token = Token(
                text=word, start_position=start_pos, whitespace_after=True
            )
            tokens.append(token)

            if (previous_token is not None) and (
                    token.start_pos - 1
                    == previous_token.start_pos + len(previous_token.text)
            ):
                previous_token.whitespace_after = False

            previous_token = token
        return tokens

    return tokenizer


def flair_moses_tokenizer():
    # TODO: Make PR with these changes
    moses_tokenizer = MosesTokenizerSpans(lang="fr")
    moses_tokenizer = build_moses_tokenizer(tokenizer=moses_tokenizer)
    return moses_tokenizer


def sent_tokenizer(text):
    return text.split("\n")


def app_page_layout(page_layout,
                    app_title="Dash Etalab App",
                    app_name="",
                    light_logo=True,
                    standalone=False,
                    bg_color="#506784",
                    font_color="#F3F6FA"):
    return html.Div(
        id='main_page',
        children=[
            dcc.Location(id='url', refresh=False),
            html.Div(
                id='app-page-header',
                children=[
                    html.A(
                        id='dashbio-logo', children=[
                            html.Img(
                                src="./assets/Data_gouv_fr_logo.svg"

                            )],
                        href="https://www.etalab.gouv.fr/"
                    ),
                    html.H2(
                        app_title
                    ),

                    html.A(
                        id='gh-link',
                        children=[
                            'Voir sur Github'
                        ],
                        href="https://github.com/etalab-ia",
                        style={'color': 'white' if light_logo else 'black',
                               'border': 'solid 1px white' if light_logo else 'solid 1px black'}
                    ),

                    html.Img(
                        src='data:image/png;base64,{}'.format(
                            base64.b64encode(
                                open(
                                    './assets/GitHub-Mark-{}64px.png'.format(
                                        'Light-' if light_logo else ''
                                    ),
                                    'rb'
                                ).read()
                            ).decode()
                        )
                    )
                ],
                style={
                    'background': bg_color,
                    'color': font_color,
                }
            ),
            html.Div(
                id='app-page-content',
                children=page_layout
            )
        ],
    )


def run_standalone_app(
        layout,
        callbacks,
        header_colors,
        filename
):
    """Run demo app (tests/dashbio_demos/*/app.py) as standalone app."""
    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

    app.scripts.config.serve_locally = True
    # Handle callback to component with id "fullband-switch"
    app.config['suppress_callback_exceptions'] = True

    # Get all information from filename

    app_name = "Etalab Pseudonymisation"

    app_title = "{}".format(app_name.replace('-', ' ').title())

    # Assign layout
    app.layout = app_page_layout(
        page_layout=layout(),
        app_title=app_title,
        app_name=app_name,
        standalone=True,
        **header_colors()
    )

    # Register all callbacks
    callbacks(app)

    # return app object
    return app


flair_moses_tokenize = flair_moses_tokenizer()

ENTITIES = {"PER_PRENOM": "PRENOM", "PER_NOM": "NOM", "LOC": "ADRESSE"}


def prepare_html(sentences_tagged, original_text):
    singles = [f"{letter}..." for letter in ascii_uppercase]
    doubles = [f"{a}{b}..." for a, b in list(itertools.combinations(ascii_uppercase, 2))]
    pseudos = singles + doubles
    pseudo_entity_dict = {}
    sentences_pseudonymized = copy.deepcopy(sentences_tagged)

    def generate_html_components(senteces, original_text):
        html_components = []
        for i_sent, sent in enumerate(senteces):
            sent_span = sent.get_spans("ner")
            if not sent_span:
                html_components.append(html.P(sent.to_original_text()))
            else:
                temp_list = []
                index = 0
                for span in sent_span:
                    start = span.start_pos
                    end = span.end_pos
                    temp_list.append(original_text[i_sent][index:start])
                    index = end
                    temp_list.append(
                        html.Mark(children=span.text, **{"data-entity": ENTITIES[span.tag], "data-index": ""}))
                temp_list.append(original_text[i_sent][index:])
                html_components.append(html.P(temp_list))
        return html_components

    for id_sn, sent in enumerate(sentences_pseudonymized):
        for sent_span in sent.get_spans("ner"):
            if "LOC" in sent_span.tag:
                for id_tok in range(len(sent_span.tokens)):
                    sent_span.tokens[id_tok].text = "..."
            else:
                pass
                for id_tok, token in enumerate(sent_span.tokens):
                    replacement = pseudo_entity_dict.get(token.text.lower(), pseudos.pop(0))
                    pseudo_entity_dict[token.text.lower()] = replacement
                    sent_span.tokens[id_tok].text = replacement

    html_components_anonym = generate_html_components(senteces=sentences_pseudonymized,
                                                      original_text=original_text)
    html_components_tagged = generate_html_components(senteces=sentences_tagged,
                                                      original_text=original_text)
    return html_components_anonym, html_components_tagged


def create_html_outputs(text, tagger, word_tokenizer=None):
    if not word_tokenizer:
        tokenizer = flair_moses_tokenize

    text = [t.strip() for t in text.split("\n") if t.strip()]

    sentences_tagged = tagger.predict(sentences=text,
                                      mini_batch_size=32,
                                      embedding_storage_mode="cpu",
                                      use_tokenizer=tokenizer,
                                      verbose=True)

    html_pseudoynmized, html_tagged = prepare_html(sentences_tagged=sentences_tagged,
                                                   original_text=text)

    return html_pseudoynmized, html_tagged


def file2txt(doc_path: str):
    if doc_path.endswith("doc"):
        result = subprocess.run(['antiword', '-w', '0', doc_path], stdout=subprocess.PIPE)
        result = result.stdout.decode("utf-8").replace("|", "\t")
    else:
        result = textract.process(doc_path, encoding='utf-8').decode("utf8").replace("|", "\t")
    return result


def load_text(doc_path):
    return file2txt(doc_path)


def build_pseudonymisation_map_flair(sentences, pseudos, acceptance_score, tags="all"):
    """
    Gets all replacements to be made in pseudonymized text using flair tagged sentences

    :param sentences: list of tuples (flair tagged sentences, original)
    :param pseudos: list of pseudos to be used
    :param acceptance_score: minimum confidence score to accept NER tag
    :return: dict: keys are spans in sentence, values are pseudos
    """

    replacements = {}
    mapping = {}
    for sentence in sentences:
        for token in sentence:
            entity = token.get_tag("ner").value
            if entity != 'O' and (entity in tags or tags == "all"):
                entity = entity[2:]
                if "LOC" not in entity:
                    if token.text.lower() not in mapping:
                        mapping[token.text.lower()] = pseudos.pop(0)

                    replacements[sentence[token.idx - 1]] = mapping[token.text.lower()]
                else:
                    replacements[sentence[token.idx - 1]] = "..."

    return replacements
