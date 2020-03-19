import pandas as pd
import os
import textract
import xml.etree.ElementTree as ET
from data.write_database import write_data
from data.clean_xml import make_utf8_corrections
from data.match_tags import match_pseudonymes
from joblib import Parallel, delayed
from tqdm import tqdm
import nltk
from nltk.tokenize import WordPunctTokenizer
import config


path_to_document_csv = config.paths["csv_sql"]
path_to_files = config.paths["raw_files"]

def get_correct_line(df_decisions):
    """
    The passed df has repeated lines for the same file (same chemin_source).
    We take the most recent one.
    :param df_decisions: Dataframe of decisions
    :return: Dataframe without repeated lines (according to the chemin_source column)
    """
    return df_decisions.sort_values('timestamp_modification').drop_duplicates('chemin_source', keep='last')


def convert_file(row):
    source_path = (row["chemin_source"]).replace("\\", "/")  # Windows path -> Linux path cool hack

    if "manuel" in source_path:
        source_path = "/".join(source_path.split("/")[1:]).lower()
        if os.path.isfile(path_to_files + source_path):
            return path_to_files + source_path
    else:
        source_path = "/".join(source_path.split("/")[3:])  # Remove server name from path
        if os.path.isfile(path_to_files + source_path):
            return path_to_files + source_path

    return False


only_corriges = True

# A FACTORISER

decisions_csv = path_to_document_csv
df_decisions = pd.read_csv(decisions_csv)
if only_corriges:
    df_decisions = df_decisions[df_decisions.statut == 5]

df_decisions = get_correct_line(df_decisions)
#df_decisions = df_decisions[df_decisions.statut == 5]


def process_file(row,sent_tokenizer, word_tokenizer):
    path = convert_file(row)
    id_ = row["id"]


    if path :
        try:

            text = textract.process(path, encoding='utf-8').decode("utf8").replace("),", ") ,") #hack hoprrible pour gérer la tokenisation des ),
            root = ET.ElementTree(ET.fromstring(make_utf8_corrections(row["detail_anonymisation"])))


            matched_pseudonymes = match_pseudonymes(root, text, path)

            if matched_pseudonymes:
                write_data(text, matched_pseudonymes, id_, sent_tokenizer, word_tokenizer)
            else:
                pass
                # ici lister les erreurs

        except Exception as e:
           print(e)

if __name__ == '__main__':
    n_jobs=14
    language_punkt_vars = nltk.tokenize.punkt.PunktLanguageVars
    language_punkt_vars.sent_end_chars = (";", ".", ":")
    word_tokenizer = WordPunctTokenizer()
    custom_sent_tokenizer = nltk.tokenize.PunktSentenceTokenizer("nltk_data/tokenizers/punkt/french.pickle")
    #nlp = spacy.load('fr_core_news_sm')  # bouger ca hors de la fontion
    #Parallel(n_jobs=n_jobs)(delayed(process_file)(row, custom_sent_tokenizer, word_tokenizer, path_to_files) for index, row in tqdm(df_decisions.iterrows()))
    pathd = "/Users/thomasclavier/.Trash/IN/DCA/136/2014/20140526/14MA00766.doc"

    for index, row in df_decisions.iterrows():
        path = convert_file(row)
        if path == pathd:
            break

    process_file(row, custom_sent_tokenizer, word_tokenizer)