import os
import base64
import sys
from hashlib import md5
from typing import Dict

import dash_interface.helper
from dash_interface.components.tab_about import tab_about_content
from dash_interface.components.tab_errors import tab_errors_content, pane_errors_content, ERROR_PANE_TEXT_STATS, \
    DATASETS_STATS, ERROR_PANE_TAGGED_TEXT
from dash_interface.components.tab_upload import tab_upload_content

sys.path.append("../")

from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
from dash_interface.helper import run_standalone_app, tagger

DATAPATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
ERROR_FILE_DICT = []


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
        dcc.Store(id='session-store', storage_type='session'),
        html.Div(id='seq-view-control-tabs',
                 className="four columns div-user-controls",
                 children=[
                     dbc.Tabs(id='main-tabs', children=[
                         tab_about_content,
                         tab_upload_content,
                         tab_errors_content
                     ], active_tab="tab-about"),
                 ]),
        dbc.Container(id='right-pane', className="seven columns", fluid=True)
    ])
    return div


def callbacks(_app):
    """ Define callbacks to be executed on page change"""

    @_app.callback([Output("error-pane", 'children'),
                    Output("errors", 'children'),
                    Output("dataset-stats", 'children')],
                   [Input('error-slider', 'value')])
    def error_slider_update(value):
        dict_values = {80: 0, 160: 1, 400: 2, 600: 3, 800: 4, 1200: 5,
                       1600: 6, 2400: 7}
        errors_stats = ERROR_PANE_TEXT_STATS[dict_values[value]]
        dataset_stats = DATASETS_STATS[dict_values[value]]
        errors = dcc.Markdown(f"""
            * Nombre d'entités sous-reperées (un nom non trouvée par le modèle): {errors_stats["under_classifications"]}
            * Nombre d'entités sur-reperées (le nom d'un greffier trouvé par le système): {errors_stats["over_classifications"]}
            * Nombre d'entités mal reperées (un nom identifié comme un prènom): {errors_stats["miss_classifications"]}
            * Nombre d'entités bien reperées (un nom bien identifié): {errors_stats["correct_classifications"]}
            """)

        stats_dataset = dcc.Markdown(f"""
            * Noms annotés : {dataset_stats[1]}
            * Prènoms annotés : {dataset_stats[2]}
            * Adresses annotées : {dataset_stats[0]}
            """)

        return html.Div(ERROR_PANE_TAGGED_TEXT[dict_values[value]]), errors, stats_dataset

    @_app.callback([Output('right-pane', 'children'),
                    Output('session-store', 'data')],
                   [Input('upload-data', 'contents'),
                    Input('upload-data', 'filename'),
                    Input("main-tabs", "active_tab")],
                   [State('session-store', 'data')])
    def pseudo_pane_update(contents, file_name: str, tab_is_at, data: Dict):

        if tab_is_at == "tab-about":
            return None, data
        elif tab_is_at == "tab-errors":
            return pane_errors_content, data
        if contents is None:
            return html.Div("Chargez un fichier dans l'onglet données pour le faire apparaitre pseudonymisé ici",
                            style={"width": "100%", "display": "flex", "align-items": "center",
                                   "justify-content": "center"}), data



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


if __name__ == '__main__':
    app = run_standalone_app(layout, callbacks, header_colors, __file__)
    #
    app.run_server(debug=False, port=8050)
    pass
