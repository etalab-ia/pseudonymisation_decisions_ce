import os
import sys
from typing import Dict

import dash_interface.helper
from dash_interface.components.tab_about import tab_about_content
from dash_interface.components.tab_errors import tab_errors_content, pane_errors_content, ERROR_PANE_TEXT_STATS, \
    DATASETS_STATS, ERROR_PANE_TAGGED_TEXT, pane_errors_content_dynamic
from dash_interface.components.tab_upload import tab_upload_content, pane_upload_content

sys.path.append("../")

from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
from dash_interface.helper import run_standalone_app

DATAPATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')

def layout():
    """
    Returns page layout. Modifications of page structure should be passed here
    :return:  Layout
    """
    div = html.Div(id='seq-view-body', className='app-body', children=[
        dcc.Store(id='session-store', storage_type='session'),
        html.Div(id='seq-view-control-tabs',
                 className="five columns div-user-controls",
                 children=dbc.Container(
                     dbc.Tabs(id='main-tabs', children=[
                         tab_about_content,
                         tab_upload_content,
                         tab_errors_content
                     ], active_tab="tab-about"),
                 )),
        dbc.Container(id='right-pane', className="six columns", fluid=True)
    ])
    return div


def callbacks(_app):
    """ Define callbacks to be executed on page change"""

    @_app.callback([Output("error-pane", 'children'),
                    Output("errors", 'children'),
                    Output("dataset-stats", 'children')],
                   [Input('error-slider', 'value')])
    def error_slider_update(value):
        error_text_children, errors_children, dataset_errors_children = pane_errors_content_dynamic(value)
        return error_text_children, errors_children, dataset_errors_children

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
        elif tab_is_at == "tab-upload":
            children, data = pane_upload_content(contents, file_name, data)
            return children, data


if __name__ == '__main__':
    app = run_standalone_app(layout, callbacks)
    app.run_server(debug=False, port=8050)
