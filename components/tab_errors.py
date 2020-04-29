import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

from dash_interface.prepare_data import prepare_error_pane

ERROR_PANE_TAGGED_TEXT, ERROR_PANE_TEXT_STATS, DATASETS_STATS = prepare_error_pane()

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