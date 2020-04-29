import base64
from hashlib import md5
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

from dash_interface.helper import tagger

tab_upload_content = dbc.Tab(
    label='Données',
    tab_id="tab-upload",
    children=html.Div(className='control-tab', children=[
        html.Div("Veuiller choisir un fichier (type .doc, .docx, .txt. Max 200 Ko)",
                 className='app-controls-block'),

        html.Div(
            id='seq-view-fast-upload',
            children=[
                dcc.Upload(
                    id='upload-data',
                    className='control-upload',
                    max_size="200000",  # 200 kb
                    children=html.Div([
                        "Faire glisser ou cliquer pour charger un fichier"
                    ]),
                ),
            ]
        ),

    ])
)


def pane_upload_content(dash_interface, contents, file_name, data):
    if contents is None:
        return html.Div("Chargez un fichier dans l'onglet données pour le faire apparaitre pseudonymisé ici",
                        style={"width": "100%", "display": "flex", "align-items": "center",
                               "justify-content": "center"}), data
    else:
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
        decoded = dash_interface.helper.load_text(temp_path)

        html_pseudoynmized, html_tagged = dash_interface.helper.create_tab_2_html_outputs(text=decoded, tagger=tagger)
        children = dbc.Container(
            [
                html.H4("Document annotée"),
                dbc.Row([dbc.Col(html.Div(children=html_tagged, id="text-output-tagged", style={"maxHeight": "500px",
                                                                                                "overflow-y": "scroll"}))],
                        className="h-50", style={"margin-bottom": "2cm"}),

                html.H4("Document pseudonymisé"),
                dbc.Row([dbc.Col(html.Div(children=html_pseudoynmized,
                                          id="text-output-anonym", style={"maxHeight": "500px",
                                                                          "overflow-y": "scroll"}))],
                        className="h-50"),
            ], style={"height": "100vh"}, fluid=True)

        data.clear()
        data[content_id] = children
        return children, data
