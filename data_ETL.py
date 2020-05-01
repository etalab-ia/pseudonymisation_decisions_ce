import copy
import glob
import itertools
import subprocess
from pathlib import Path
from string import ascii_uppercase
from typing import Callable, List

import dash_html_components as html
import pandas as pd
import textract
from flair.data import Token
from flair.datasets import ColumnDataset
from sacremoses import MosesTokenizer, MosesDetokenizer, MosesPunctNormalizer


def prepare_upload_tab_html(sentences_tagged, original_text):
    singles = [f"{letter}..." for letter in ascii_uppercase]
    doubles = [f"{a}{b}..." for a, b in list(itertools.combinations(ascii_uppercase, 2))]
    pseudos = singles + doubles
    pseudo_entity_dict = {}
    sentences_pseudonymized = copy.deepcopy(sentences_tagged)

    def generate_upload_tab_html_components(sentences, original_text):
        html_components = []
        for i_sent, sent in enumerate(sentences):
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

    html_components_anonym = generate_upload_tab_html_components(sentences=sentences_pseudonymized,
                                                                 original_text=original_text)
    html_components_tagged = generate_upload_tab_html_components(sentences=sentences_tagged,
                                                                 original_text=original_text)
    return html_components_anonym, html_components_tagged


def create_upload_tab_html_output(text, tagger, word_tokenizer=None):
    if not word_tokenizer:
        tokenizer = MOSES_TOKENIZER

    text = [t.strip() for t in text.split("\n") if t.strip()]

    sentences_tagged = tagger.predict(sentences=text,
                                      mini_batch_size=32,
                                      embedding_storage_mode="none",
                                      use_tokenizer=tokenizer,
                                      verbose=True)

    html_pseudoynmized, html_tagged = prepare_upload_tab_html(sentences_tagged=sentences_tagged,
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


ENTITIES = {"PER_PRENOM": "PRENOM", "PER_NOM": "NOM", "LOC": "ADRESSE"}


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

MOSES_TOKENIZER = build_moses_tokenizer(tokenizer=MosesTokenizerSpans(lang="fr"))


# def flair_moses_tokenizer():
#     moses_tokenizer = MosesTokenizerSpans(lang="fr")
#     moses_tokenizer = build_moses_tokenizer(tokenizer=moses_tokenizer)
#     return moses_tokenizer


def sent_tokenizer(text):
    return text.split("\n")


def add_positions_to_dataset(dataset: ColumnDataset):
    for i_sent, sentence in enumerate(dataset.sentences):
        for i_tok, token in enumerate(sentence.tokens):
            token: Token = token
            if i_tok == 0:
                token.start_pos = 0
            else:
                prev_token = sentence.tokens[i_tok - 1]
                token.start_pos = prev_token.end_pos + 1
            token.end_pos = token.start_pos + len(token.text) - (1 if i_tok >= len(sentence.tokens) - 1 else 0)
    pass


def prepare_error_decisions(decisions_path: Path):
    error_files = glob.glob(decisions_path.as_posix() + "/*.txt")
    dict_df = {}
    dict_stats = {}
    for error_file in error_files:
        df_error = pd.read_csv(error_file, sep="\t", engine="python", skip_blank_lines=False,
                               names=["token", "true_tag", "pred_tag"]).fillna("")
        df_no_spaces = df_error[df_error["token"] != ""]

        under_pseudonymization = df_no_spaces[(df_no_spaces["true_tag"] != df_no_spaces["pred_tag"])
                                              & (df_no_spaces["true_tag"] != "O")]
        miss_pseudonymization = df_no_spaces[(df_no_spaces["true_tag"] != df_no_spaces["pred_tag"])
                                             & (df_no_spaces["true_tag"] != "O")
                                             & (df_no_spaces["pred_tag"] != "O")]
        over_pseudonymization = df_no_spaces[(df_no_spaces["true_tag"] != df_no_spaces["pred_tag"])
                                             & (df_no_spaces["true_tag"] == "O")]
        correct_pseudonymization = df_no_spaces[(df_no_spaces["true_tag"] == df_no_spaces["pred_tag"])
                                                & (df_no_spaces["true_tag"] != "O")]

        df_error["display_col"] = "O"
        if not correct_pseudonymization.empty:
            df_error.loc[correct_pseudonymization.index, "display_col"] = correct_pseudonymization['pred_tag'] + "_C"
        if not under_pseudonymization.empty:
            df_error.loc[under_pseudonymization.index, "display_col"] = under_pseudonymization["pred_tag"] + "_E"
        if not miss_pseudonymization.empty:
            df_error.loc[miss_pseudonymization.index, "display_col"] = miss_pseudonymization["pred_tag"] + "_E"
        if not over_pseudonymization.empty:
            df_error.loc[over_pseudonymization.index, "display_col"] = over_pseudonymization["pred_tag"] + "_E"
        df_error.loc[df_error["token"] == "", "display_col"] = ""

        # Get simple stats
        nb_noms = len(df_error[df_error["true_tag"].str.startswith("B-PER_NOM")])
        nb_prenoms = len(df_error[df_error["true_tag"].str.startswith("B-PER_PRENOM")])
        nb_loc = len(df_error[df_error["true_tag"].str.startswith("B-LOC")])

        serie_stats = pd.Series({"nb_noms": nb_noms, "nb_prenoms": nb_prenoms, "nb_loc": nb_loc,
                                 "under_classifications": len(under_pseudonymization),
                                 "over_classifications": len(over_pseudonymization),
                                 "miss_classifications": len(miss_pseudonymization),
                                 "correct_classifications": len(correct_pseudonymization)})

        dict_df[error_file.split("/")[-1]] = df_error.loc[:, ["token", "display_col"]]
        dict_stats[error_file.split("/")[-1]] = serie_stats

    return dict_df, dict_stats