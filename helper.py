import base64

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html


def app_page_layout(page_layout, app_title="Etalab Pseudo", app_name="", light_logo=False, standalone=False,
                    bg_color="#506784", font_color="#F3F6FA"):
    return html.Div(
        id='main_page',
        children=[
            dcc.Location(id='url', refresh=False),
            html.Div(
                id='app-page-header',
                children=[
                    html.A(
                        id='dashbio-logo', children=[
                            html.Img(
                                src="./assets/MarianneLogo-3-90x57.png"

                            )],
                        href="https://www.etalab.gouv.fr/"
                    ),
                    html.H2([app_title, html.Sup("β")], style={"font-family": 'Open Sans', "font-weight": "400"}),

                    html.A(
                        id='gh-link',
                        children=[
                            'Voir sur Github'
                        ],
                        href="https://github.com/etalab-ia",
                        style={'color': 'white' if light_logo else 'black',
                               'border': 'solid 1px white' if light_logo else 'solid 1px black'}
                    ),

                    html.Img(
                        src='data:image/png;base64,{}'.format(
                            base64.b64encode(
                                open(
                                    './assets/GitHub-Mark-{}64px.png'.format(
                                        'Light-' if light_logo else ''
                                    ),
                                    'rb'
                                ).read()
                            ).decode()
                        )
                    )
                ],
                style={
                    'background': bg_color,
                    'color': font_color,
                    "border-bottom-color": "#eaeaea",
                    "border-bottom-style": "solid"
                }

            ),
            html.Div(
                id='app-page-content',
                children=page_layout
            )
        ],
    )


def run_standalone_app(layout, callbacks):
    """Run demo app (tests/dashbio_demos/*/app.py) as standalone app."""
    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

    app.title = "Etalab Pseudo"
    app.scripts.config.serve_locally = True
    # Handle callback to component with id "fullband-switch"
    app.config['suppress_callback_exceptions'] = True

    # Get all information from filename

    app_name = "Pseudonymisation Demo"

    app_title = "{}".format(app_name.replace('-', ' ').title())

    header_colors = {
        'bg_color': 'white',
        'font_color': 'black'
    }

    # Assign layout
    app.layout = app_page_layout(
        page_layout=layout(),
        app_title=app_title,
        app_name=app_name,
        standalone=True,
        **header_colors
    )

    # Register all callbacks
    callbacks(app)

    # return app object
    return app
