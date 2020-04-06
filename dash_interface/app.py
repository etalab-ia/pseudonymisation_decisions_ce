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

    return html.Div(id='seq-view-body', className='app-body', children=[
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
                         # dcc.Tab(
                         #     label='Options',
                         #     value='sequence',
                         #     children=html.Div(className='control-tab', children=[
                         #         html.Div(
                         #             id='seq-view-entry-dropdown-container',
                         #             className='app-controls-block',
                         #             children=[
                         #                 html.Div(
                         #                     "View entry:",
                         #                     className='app-controls-name'
                         #                 ),
                         #                 dcc.Dropdown(
                         #                     className='app-dropdown',
                         #                     id='fasta-entry-dropdown',
                         #                     options=[
                         #                         {'label': 1, 'value': 0}
                         #                     ],
                         #                     value=0
                         #                 ),
                         #                 html.Div(
                         #                     id='seq-view-number-entries',
                         #                     className='app-controls-desc'
                         #                 )
                         #             ]
                         #         ),
                         #         html.Br(),
                         #         html.Div(
                         #             id='seq-view-sel-or-cov-container',
                         #             children=[
                         #                 html.Div(
                         #                     "Selection or coverage:",
                         #                     className='app-controls-name'
                         #                 ),
                         #                 dcc.RadioItems(
                         #                     id='selection-or-coverage',
                         #                     options=[
                         #                         {
                         #                             'label': 'selection',
                         #                             'value': 'sel'
                         #                         },
                         #                         {
                         #                             'label': 'coverage',
                         #                             'value': 'cov'
                         #                         }
                         #                     ],
                         #                     value='sel'
                         #                 )
                         #             ]
                         #         ),
                         #
                         #         html.Hr(),
                         #
                         #         html.Div(id='cov-options', children=[
                         #             html.Div(className='app-controls-block', children=[
                         #                 html.Div(
                         #                     "Add coverage from selection by:",
                         #                     className='app-controls-name'
                         #                 ),
                         #                 dcc.RadioItems(
                         #                     id='mouse-sel-or-subpart-sel',
                         #                     options=[
                         #                         {'label': 'mouse',
                         #                          'value': 'mouse'},
                         #                         {'label': 'search',
                         #                          'value': 'subpart'}
                         #                     ],
                         #                     value='mouse'
                         #                 ),
                         #             ]),
                         #
                         #             html.Div(className='app-controls-block', children=[
                         #                 html.Div(
                         #                     "Text color:",
                         #                     className='app-controls-name'
                         #                 ),
                         #                 dcc.Input(
                         #                     id='coverage-color',
                         #                     type='text',
                         #                     value='rgb(255, 0, 0)'
                         #                 )
                         #             ]),
                         #             html.Div(className='app-controls-block', children=[
                         #                 html.Div(
                         #                     "Background color:",
                         #                     className='app-controls-name'
                         #                 ),
                         #                 dcc.Input(
                         #                     id='coverage-bg-color',
                         #                     type='text',
                         #                     value='rgb(0, 0, 255)'
                         #                 ),
                         #             ]),
                         #             html.Div(className='app-controls-block', children=[
                         #                 html.Div(
                         #                     "Tooltip:",
                         #                     className='app-controls-name'
                         #                 ),
                         #                 dcc.Input(
                         #                     id='coverage-tooltip',
                         #                     type='text',
                         #                     value='',
                         #                     placeholder='hover text'
                         #                 ),
                         #             ]),
                         #             html.Div(className='app-controls-block', children=[
                         #                 html.Div(
                         #                     "Underscore text: ",
                         #                     className='app-controls-name'
                         #                 ),
                         #                 dcc.Checklist(
                         #                     id='coverage-underscore',
                         #                     options=[
                         #                         {'label': '',
                         #                          'value': 'underscore'}
                         #                     ],
                         #                     value=[]
                         #                 )
                         #             ]),
                         #             html.Div(className='app-controls-block', children=[
                         #                 html.Button(
                         #                     id='coverage-submit',
                         #                     children='Submit'
                         #                 ),
                         #                 html.Button(
                         #                     id='coverage-reset',
                         #                     children='Reset'
                         #                 )
                         #             ])
                         #         ]),
                         #
                         #         html.Div(id='seq-view-sel-slider-container', children=[
                         #             html.Div(className='app-controls-block', children=[
                         #                 html.Div(
                         #                     className='app-controls-name',
                         #                     children="Selection region:"
                         #                 ),
                         #                 dcc.RadioItems(
                         #                     id='sel-slider-or-input',
                         #                     options=[
                         #                         {'label': 'slider', 'value': 'slider'},
                         #                         {'label': 'input', 'value': 'input'}
                         #                     ],
                         #                     value='slider'
                         #                 )
                         #             ]),
                         #             html.Div(className='app-controls-block', children=[
                         #                 dcc.RangeSlider(
                         #                     id='sel-slider',
                         #                     min=0,
                         #                     max=0,
                         #                     step=1,
                         #                     value=[0, 0]
                         #                 )
                         #             ]),
                         #             html.Div(className='app-controls-block', children=[
                         #                 # optional numeric input for longer sequences
                         #                 html.Div(
                         #                     id='sel-region-inputs',
                         #                     children=[
                         #                         "From: ",
                         #                         dcc.Input(
                         #                             id='sel-region-low',
                         #                             type='number',
                         #                             min=0,
                         #                             max=0,
                         #                             placeholder="low"
                         #                         ),
                         #                         "To: ",
                         #                         dcc.Input(
                         #                             id='sel-region-high',
                         #                             type='number',
                         #                             min=0,
                         #                             max=0,
                         #                             placeholder="high"
                         #                         ),
                         #                     ],
                         #                     style={'display': 'none'}
                         #                 )
                         #             ]),
                         #
                         #             html.Div(
                         #                 id='seq-view-dna-or-protein-container',
                         #                 children=[
                         #                     html.Div(className='app-controls-block', children=[
                         #                         html.Div(
                         #                             className='app-controls-name',
                         #                             children="Translate selection from:"
                         #                         ),
                         #                         dcc.Dropdown(
                         #                             id='translation-alphabet',
                         #                             options=[
                         #                                 {'label': 'DNA',
                         #                                  'value': 'dna'},
                         #                                 {'label': 'RNA',
                         #                                  'value': 'rna'}
                         #                             ],
                         #                             value=None
                         #                         )
                         #                     ])
                         #                 ]
                         #             ),
                         #
                         #             html.Div(
                         #                 className='app-controls-name',
                         #                 children="Selection highlight color:"
                         #             ),
                         #             dcc.Dropdown(
                         #                 className='app-dropdown',
                         #                 id='sel-color',
                         #                 options=[
                         #                     {'label': 'violet', 'value': 'violet'},
                         #                     {'label': 'indigo', 'value': 'indigo'},
                         #                     {'label': 'blue', 'value': 'blue'},
                         #                     {'label': 'green', 'value': 'green'},
                         #                     {'label': 'yellow', 'value': 'yellow'},
                         #                     {'label': 'orange', 'value': 'orange'},
                         #                     {'label': 'red', 'value': 'red'}
                         #                 ],
                         #                 value='indigo'
                         #             )
                         #         ])
                         #     ])
                         # )
                     ]),
                 ]),
        html.Div(id='seq-view-control',
                 className="seven columns div-user-controls",
                 children=html.Div(className='page',id="text-output")),
    ])


def callbacks(_app):
    """ Define callbacks to be executed on page change"""



    @_app.callback(Output('text-output', 'children'),
                  [Input('upload-data', 'contents'),
                  Input('upload-data', 'filename'),
                   Input('upload-data', 'last_modified')])
    def update_sequence(content, list_of_names, list_of_dates):

        if content == None:

            return html.Div("Chargez un fichier dans l'onglet données pour le faire apparaitre pseudonymisé ici", style = {"width": "100%", "display": "flex", "align-items": "center", "justify-content": "center"})

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
    app.run_server(debug=True, port=8050)
