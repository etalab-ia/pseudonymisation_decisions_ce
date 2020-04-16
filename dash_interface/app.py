import os
import base64
import sys

sys.path.append("../")

from dash.dependencies import Input, Output, State
import dash_html_components as html
import dash_core_components as dcc
import run.process_file as pf
from dash_interface.helper import run_standalone_app, sent_tokenizer, word_tokenizer, tagger

DATAPATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')


def header_colors():
    return {
        'bg_color': '#0055A4',
        'font_color': 'white'
    }


def description():
    return "Test d'une application de pseudonimysation pour le Lab IA"


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
                         dcc.Tab(
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
                         ),
                         dcc.Tab(
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
                                     id='seq-view-fasta-upload',
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
                         ),
                         dcc.Tab(
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
                     ]),
                 ]),
        html.Div(id='seq-view-control',
                 className="seven columns div-user-controls",
                 children=html.Div(className='page', id="text-output")),
    ])
    return div


def callbacks(_app):
    """ Define callbacks to be executed on page change"""

    @_app.callback(Output('text-output', 'chil  dren'),
                   [Input('upload-data', 'contents'),
                    Input('upload-data', 'filename'),
                    Input('upload-data', 'last_modified')])
    def update_sequence(content, list_of_file_names, list_of_dates):
        if content == None:
            return html.Div("Chargez un fichier dans l'onglet données pour le faire apparaitre pseudonymisé ici",
                            style={"width": "100%", "display": "flex", "align-items": "center",
                                   "justify-content": "center"})

        content_type, content_string = content.split(',')
        decoded = base64.b64decode(content_string)
        f = open('/tmp/output.doc', 'wb')
        f.write(decoded)
        f.close()
        decoded = pf.load_text('/tmp/output.doc')

        pseudo = pf.create_html_file(decoded, sent_tokenizer, word_tokenizer, tagger)

        return pseudo


# only declare app/server if the file is being run directly
if 'DEMO_STANDALONE' not in os.environ:
    app = run_standalone_app(layout, callbacks, header_colors, __file__)
    server = app.server

if __name__ == '__main__':
    app.run_server(debug=False, port=8050)
