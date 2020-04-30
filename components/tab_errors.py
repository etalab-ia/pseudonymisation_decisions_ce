import glob
from pathlib import Path

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from flair.datasets import ColumnDataset
from pandas import DataFrame

from dash_interface.data_ETL import add_positions_to_dataset

ORDERED_FILENAMES = ["80_10_10.results.txt",
                     "160_20_20.results.txt",
                     "400_50_50.results.txt",
                     "600_75_75.results.txt",
                     "800_100_100.results.txt",
                     "1200_150_150.results.txt",
                     "1600_200_200.results.txt",
                     "2400_300_300.results.txt"]

tab_errors_content = dbc.Tab(
    label='Errors',
    tab_id="tab-errors",
    children=html.Div(className='page', children=[
        html.H4(className='what-is', children="Visualisation d'erreures"),
        html.P("Mais combien des données j'en ai besoin pour entrainer un modele similaire ?"
               "Ici on vous montre les differences par rapport a la taille du corpus d'entrainement"),
        html.Br(),

    ])
)
pane_errors_content = [
    html.H5("Choose a model:"),
    dbc.Container(dcc.Slider(min=80, step=None, max=2400, id="error-slider", marks={80: '80', 160: '160',
                                                                                    400: '400', 600: '600',
                                                                                    800: '800', 1200: '1200',
                                                                                    1600: '1600', 2400: '2400'},
                             value=80), style={"margin-bottom": "1cm"}),
    # html.H5("Error display:"),
    dbc.Container(id="error-pane", style={"maxHeight": "350px", "overflow-y": "scroll", "margin-bottom": "1cm"},
                  fluid=True),
    html.H5("Erreures"),
    dbc.Container(id="errors"),
    html.H5("Annotations du dataset d'entraînement"),
    dbc.Container(id="dataset-stats"),

]

def pane_errors_content_dynamic(value):
    dict_values = {80: 0, 160: 1, 400: 2, 600: 3, 800: 4, 1200: 5,
                       1600: 6, 2400: 7}
    errors_stats = ERROR_PANE_TEXT_STATS[dict_values[value]]
    dataset_stats = DATASETS_STATS[dict_values[value]]
    errors_children = dcc.Markdown(f"""
        * Nombre d'entités sous-reperées (un nom non trouvée par le modèle): {errors_stats["under_classifications"]}
        * Nombre d'entités sur-reperées (le nom d'un greffier trouvé par le système): {errors_stats["over_classifications"]}
        * Nombre d'entités mal reperées (un nom identifié comme un prènom): {errors_stats["miss_classifications"]}
        * Nombre d'entités bien reperées (un nom bien identifié): {errors_stats["correct_classifications"]}
        """)

    dataset_errors_children = dcc.Markdown(f"""
        * Noms annotés : {dataset_stats[1]}
        * Prènoms annotés : {dataset_stats[2]}
        * Adresses annotées : {dataset_stats[0]}
        """)
    error_text_children = html.Div(ERROR_PANE_TAGGED_TEXT[dict_values[value]])
    return error_text_children, errors_children, dataset_errors_children

ENTITIES_DICT = {"PER_NOM": "NOM", "PER_PRENOM": "PRENOM", "LOC": "ADRESSE", "O": "NON REPERÉ"}
TEXT_FILES = "./assets/error_files"


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


def generate_errors_tab_html_components(sentences):
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
                temp_list.append(sent.to_original_text()[index:start])
                index = end
                tag = span.tag
                type_tag = tag[-1]
                new_tag = tag[:-2]
                if type_tag == "C":  # this is a correct tag. Put it in green in CSS style
                    tagged_text = html.Mark(children=span.text,
                                            **{"data-correcttab": ENTITIES_DICT[new_tag],
                                               "data-index": ""})
                elif type_tag == "E":
                    tagged_text = html.Mark(children=span.text,
                                            **{"data-errortab": ENTITIES_DICT[new_tag],
                                               "data-index": ""})
                temp_list.append(tagged_text)
            temp_list.append(sent.to_original_text()[index:])
            html_components.append(html.P(temp_list))
    return html_components


def prepare_error_pane():
    """
    This function generates the list of Dash components to show the errors produced while tagging a
    document by several trained models. The inout is a set of CoNLL annotated files (three columns: token,
    true tag, predicted tag). The output is a list of list of components describing the content of the CoNLL documents
    with P (paragraphs) and Marks (highlights). It also returns a list of dicts that contain the stats of the errors/corrects
    done by the corresponding model.

    Returns:

    """
    dict_df, data_stats = prepare_error_decisions(Path(TEXT_FILES))
    list_stats_datasets = [(2, 219, 62),
                           (3, 270, 91),
                           (12, 1112, 396),
                           (20, 1382, 296),
                           (37, 2256, 804),
                           (42, 2622, 679),
                           (58, 3982, 1112),
                           (109, 5516, 1298)]

    files_paths = []
    list_stats_errors = []
    for file_o in ORDERED_FILENAMES:
        df: DataFrame = dict_df[file_o]
        df.to_csv(f"/tmp/{file_o[:-4]}.csv", sep="\t", header=None, index=None)
        files_paths.append(f"/tmp/{file_o[:-4]}.csv")
        list_stats_errors.append(data_stats[file_o])

    flair_datasets = []
    for path in files_paths:
        temp_set = ColumnDataset(path_to_column_file=Path(path), column_name_map={0: 'text', 1: 'ner'})
        add_positions_to_dataset(temp_set)
        flair_datasets.append(temp_set)

    html_components = []
    for flair_dataset in flair_datasets:
        html_components.append(generate_errors_tab_html_components(flair_dataset))
    return html_components, list_stats_errors, list_stats_datasets


ERROR_PANE_TAGGED_TEXT, ERROR_PANE_TEXT_STATS, DATASETS_STATS = prepare_error_pane()
