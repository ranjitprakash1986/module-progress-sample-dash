# imports
from dash import dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.io as pio
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from collections import defaultdict

from datetime import *
import datetime
pio.renderers.default='iframe'
#-----------------------------------------------------------

external_stylesheets = [dbc.themes.BOOTSTRAP]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


#---------------------------------------------------
# read data
data = pd.read_csv('../data/SAMPLE_module_data.csv')

# dtype conversion
categorical_cols = ['course_id',
                   'module_id',
                   'module_name',
                   'state',
                   'student_id',
                   'student_name',
                   'items_id',
                   'items_title',
                   'items_type',
                   'items_module_id',
                   'item_cp_req_type',
                   'item_cp_req_completed',
                   'course_name']

# convert the timestamp to datetime format
# fix the column data types
data['completed_at'] = pd.to_datetime(data['completed_at'])
for col in categorical_cols:
    data[col] = data[col].astype('category')


#-----------------------------------------------------------

# Define the layout of the dashboard
# replace the figure dictionary with the function call for plotly figure plotting
app.layout = dbc.Container(
    fluid=True,
    children=[
        html.H1("Module Progress Dashboard", className="display-4"),
        dbc.Row(
            [
                dbc.Col(
                    dcc.Graph(
                        id='example1-graph',
                        figure={
                            'data': [
                                {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'Category 1'},
                                {'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': 'Category 2'},
                            ],
                            'layout': {
                                'title': 'Student Module Percent Completion'
                            }
                        }
                    )
                ),
                dbc.Col(
                    dcc.Graph(
                        id='example2-graph',
                        figure={
                            'data': [
                                {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'Category 1'},
                                {'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': 'Category 2'},
                            ],
                            'layout': {
                                'title': 'Module Completion'
                            }
                        }
                    )
                )
            ],
            className="mt-4"
        ),
        dbc.Row(
            [
                dbc.Col(
                    dcc.Graph(
                        id='example3-graph',
                        figure={
                            'data': [
                                {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'Category 1'},
                                {'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': 'Category 2'},
                            ],
                            'layout': {
                                'title': 'Item Completion'
                            }
                        }
                    )
                )
            ],
            className="mt-4"
        )
    ]
)

if __name__ == '__main__':
    app.run_server(debug=True)
