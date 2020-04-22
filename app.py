import os
import base64
import sys

from dash import dash

import dash_interface.helper

sys.path.append("../")

from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
from dash_interface.helper import run_standalone_app, tagger

DATAPATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')


def header_colors():
    return {
        'bg_color': '#0055A4',
        'font_color': 'white'
    }


def description():
    return "Test d'une application de pseudonimysation pour le Lab IA"


tab_about_content = dcc.Tab(
    label='À propos',
    value='what-is',
    children=html.Div(className='page', children=[
        html.H4(className='what-is', children='Pourquoi un outil de pseudonymization?'),
        html.P("Le règlement général sur la protection des données (RGPD) n’impose pas aux "
               "administrations d’anonymiser les documents qu’elles détiennent. Ainsi "
               "lorsque les "
               "documents administratifs comportent des données personnelles, ils ne peuvent "
               "être rendus publics qu'après avoir fait l'objet d'un traitement permettant "
               "de rendre impossible l'identification de ces personnes."),
        html.Br(),
        html.P("Dans l'onglet données vous pouvez charger un fichier afin de le faire "
               "pseudonimizer par l'algorithme "),

    ])
)

tab_upload_content = dcc.Tab(
    label='Données',
    value='data',
    children=html.Div(className='control-tab', children=[
        html.Div(
            id='preloaded-and-uploaded-alert',
            className='app-controls-desc',
            children=[
                'You have uploaded your own data. In order \
                to view it, please ensure that the "preloaded \
                sequences" dropdown has been cleared.'
            ],
            style={'display': 'none'}
        ),
        html.Div("Veuiller choisir un fichier",
                 className='app-controls-block'),

        html.Div(
            id='seq-view-fast-upload',
            children=[
                dcc.Upload(
                    id='upload-data',
                    className='control-upload',
                    children=html.Div([
                        "Faire glisser ou cliquer pour charger un fichier"
                    ]),
                ),
            ]
        ),

    ])
)

tab_errors_content = dcc.Tab(
    label='Errors',
    value='errors',
    children=html.Div(className='page', children=[
        html.H4(className='what-is', children="Visualisation et correction d'erreures"),
        html.P("Mais combien des données j'en ai besoin pour entrainer un modele similaire ?"
               "Ici on vous montre les differences par rapport a la taille d"),
        html.Br(),
        html.P("Dans l'onglet données vous pouvez charger un fichier afin de le faire "
               "pseudonimizer par l'algorithme "),

    ])
)


def layout():
    """
    Returns page layout. Modifications of page structure should be passed here
    :return:  Layout
    """
    div = html.Div(id='seq-view-body', className='app-body', children=[
        html.Div(id='seq-view-control-tabs',
                 className="four columns div-user-controls",
                 children=[
                     dcc.Tabs(id='seq-view-tabs', value='what-is', children=[
                         tab_about_content,
                         tab_upload_content,
                         tab_errors_content
                     ]),
                 ]),
        html.Div(id='seq-view-control', className="seven columns")
    ])
    return div


def callbacks(_app):
    """ Define callbacks to be executed on page change"""

    @_app.callback(Output('seq-view-control', 'children'),
                   [Input('upload-data', 'contents'),
                    Input('upload-data', 'filename'),
                    Input('upload-data', 'last_modified')])
    def update_sequence(content, list_of_file_names, list_of_dates):
        if content == None:
            return html.Div("Chargez un fichier dans l'onglet données pour le faire apparaitre pseudonymisé ici",
                            style={"width": "100%", "display": "flex", "align-items": "center",
                                   "justify-content": "center"})
        extension = list_of_file_names.split(".")[-1]
        temp_path = f"/tmp/output.{extension}"
        content_type, content_string = content.split(',')
        decoded = base64.b64decode(content_string)

        f = open(temp_path, 'wb')
        f.write(decoded)
        f.close()
        decoded = dash_interface.helper.load_text(temp_path)

        html_pseudoynmized, html_tagged = dash_interface.helper.create_html_outputs(text=decoded, tagger=tagger)

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
            ], style={"height": "100vh"}, className="page")

        return children


# only declare app/server if the file is being run directly
if 'DEMO_STANDALONE' not in os.environ:
    app = run_standalone_app(layout, callbacks, header_colors, __file__)
    server = app.server

if __name__ == '__main__':
    app.run_server(debug=False, port=8050)
