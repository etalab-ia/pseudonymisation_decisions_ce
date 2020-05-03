import base64
from hashlib import md5
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from flair.models import SequenceTagger

from dash_interface.data_ETL import load_text, create_upload_tab_html_output

with open("./assets/text_files/upload_example.txt", "r") as example:
    TEXTE_EXEMPLE = example.read()

TAGGER = SequenceTagger.load('/home/pavel/code/pseudo_conseil_etat/models/flair_embeds/1600_200_200/best-model.pt')

tab_upload_content = dbc.Tab(
    label='Pseudonymise un document',
    tab_id="tab-upload",
    children=html.Div(className='control-tab', children=[
        html.Div("Veuillez choisir un fichier à analyser (type .doc, .docx, .txt. Max 200 Ko)",
                 className='app-controls-block'),
        html.Div(
            id='seq-view-fast-upload',
            children=dcc.Upload(
                id='upload-data',
                className='control-upload',
                max_size="200000",  # 200 kb
                children=html.Div([
                    "Faire glisser ou cliquer pour charger un fichier"
                ]),
            ),
        ),
        html.Div(["Ou ", html.B("lancez le texte exemple en cliquant ici", id="exemple-text")],
                 className='app-controls-block'),

    ])
)


def pane_upload_content(contents, file_name, n_clicks, data):
    # if contents is None and n_clicks is None:
    #     data = data or {"n_clicks": 0}
    #     return html.Div("Chargez un fichier dans l'onglet données pour le faire apparaitre pseudonymisé ici",
    #                     style={"width": "100%", "display": "flex", "align-items": "center",
    #                            "justify-content": "center"}), data
    if n_clicks is not None and n_clicks > data["n_clicks"]:
        decoded = TEXTE_EXEMPLE
        content_id = md5(decoded.encode("utf-8")).hexdigest()
        data = data or {content_id: []}
        data["n_clicks"] = n_clicks
        if content_id in data and data[content_id]:
            children = data[content_id]
            return children, data
    elif contents:
        file_name, extension = file_name.split(".")
        temp_path = f"/tmp/output.{extension}"
        content_type, content_string = contents.split(',')

        content_id = md5(content_string.encode("utf-8")).hexdigest()

        data = data or {content_id: []}
        if content_id in data and data[content_id]:
            children = data[content_id]
            return children, data

        # If we do not have it stored, compute it
        decoded = base64.b64decode(content_string)

        f = open(temp_path, 'wb')
        f.write(decoded)
        f.close()
        decoded = load_text(temp_path)
    else:
        data = data or {"n_clicks": 0}
        return html.Div("Chargez un fichier dans l'onglet données pour le faire apparaitre pseudonymisé ici",
                        style={"width": "100%", "display": "flex", "align-items": "center",
                               "justify-content": "center"}), data

    html_pseudoynmized, html_tagged = create_upload_tab_html_output(text=decoded, tagger=TAGGER)

    pseudo_content = dbc.Card(dbc.CardBody(html_pseudoynmized),
                            style={"maxHeight": "750px", "overflow-y": "scroll",
                                   "background-color": "transparent",
                                   "font-family": 'Arial',
                                   "border": "none"},
                              )

    tagged_content = dbc.Card(dbc.CardBody(html_tagged),
                            style={"maxHeight": "750px", "overflow-y": "scroll",
                                   "font-family": 'Arial',
                                   "background-color": "transparent",
                                   "border": "none"},
                              )

    children = dbc.Tabs(
        [
            dbc.Tab(tagged_content, label="Document annotée"),
            dbc.Tab(pseudo_content, label="Document pseudonymisé"),
        ]
    )

    data = {"n_clicks": data["n_clicks"], content_id: children}
    return children, data
