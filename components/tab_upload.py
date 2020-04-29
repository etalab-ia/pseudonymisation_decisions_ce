import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

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