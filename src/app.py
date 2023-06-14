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

pio.renderers.default = "iframe"
# -----------------------------------------------------------

external_stylesheets = [dbc.themes.BOOTSTRAP]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


# ---------------------------------------------------
# reading the data
data = pd.read_csv("../data/SAMPLE_module_data.csv")

# dtype conversion
categorical_cols = [
    "course_id",
    "module_id",
    "module_name",
    "state",
    "student_id",
    "student_name",
    "items_id",
    "items_title",
    "items_type",
    "items_module_id",
    "item_cp_req_type",
    "item_cp_req_completed",
    "course_name",
]

# convert the timestamp to datetime format
# fix the column data types
data["completed_at"] = pd.to_datetime(data["completed_at"])
for col in categorical_cols:
    data[col] = data[col].astype("category")


# -----------------------------------------------------------
# global variables
# CHANGE TO MODULE ID INSTEAD OF NAME
modules = list(data.module_name.unique())
total_students = data.student_id.unique().size

# Creating a dictionary of items per module
item_dict = defaultdict()

for module in modules:
    item_dict[module] = list(data[data.module_name == module].items_title.unique())


# -------------------------------------------------------------
# Functions
def get_completed_percentage(df, module, state="completed"):
    """
    Returns the state percentage of module in df

    Input:
    ---------


    Returns:
    ---------
    """
    # CHANGE TO MODULE ID INSTEAD OF NAME
    df_module = df[df.module_name == module]
    total_module_students = df_module.student_id.unique().size
    percentage = (
        df_module[df_module.state == state].student_id.unique().size
        / total_module_students
    )
    return percentage


def module_completion_barplot(df):
    """
    Plots a horizontal barplot of student percentage module completion per module

    Input:
    -----------


    Returns:
    -----------

    """
    result = {}
    for module in modules:
        result[str(module)] = [
            round(get_completed_percentage(df, module, "unlocked") * 100, 1),
            round(get_completed_percentage(df, module, "started") * 100, 1),
            round(get_completed_percentage(df, module, "completed") * 100, 1),
        ]

    df_mod = (
        pd.DataFrame(result, index=["unlocked", "started", "completed"])
        .T.reset_index()
        .rename(columns={"index": "Module"})
    )

    # Melt the DataFrame to convert columns to rows
    melted_df = pd.melt(
        df_mod,
        id_vars="Module",
        value_vars=["unlocked", "started", "completed"],
        var_name="Status",
        value_name="Percentage Completion",
    )

    # Create a horizontal bar chart using Plotly
    fig_1 = px.bar(
        melted_df,
        y="Module",
        x="Percentage Completion",
        color="Status",
        orientation="h",
        labels={"Percentage Completion": "Percentage Completion (%)"},
        title="Percentage Completion by Students for Each Module",
        category_orders={"Module": sorted(melted_df["Module"].unique())},
    )

    # Modify the plotly configuration to change the background color
    fig_1.update_layout(
        plot_bgcolor="rgb(255, 255, 255)"  # Set the desired background color
    )

    # Convert the figure to a JSON serializable format
    fig_1_json = fig_1.to_dict()

    return fig_1_json


def get_completed_percentage_date(df, module, date):
    """
    Returns the completed percentage of a module in df until a specified date

    Inputs
    ------
    df: dataframe
    module: str, name of the module
    date: datetime.date, date till which the completion percentage of each module is desired

    Returns
    -------
    percentage: float, percentage value

    """

    # Convert the date to datetime with time component set to midnight
    datetime_date = datetime.datetime.combine(date, datetime.datetime.min.time())

    # CHANGE TO MODULE ID INSTEAD OF NAME
    df_module = df[df.module_name == module]
    total_module_students = df_module.student_id.unique().size

    # If there is not a single row with completion date then we get a datetime error since blanks are not compared to date
    # In order to get around this edge case, return 0
    if df_module[df_module.state == "completed"].size == 0:
        return 0.0

    percentage = (
        df_module[
            (df_module.state == "completed")
            & (df_module["completed_at"].dt.date <= date)
        ]
        .student_id.unique()
        .size
        / total_module_students
    )

    return percentage


def module_completion_lineplot(df):
    """
    Return a lineplot showing the percentage completion by data
    of each module

    Inputs:
    ---------


    Returns:
    --------
    """
    # To build a dashboard lineplot with time on the x axis and the percentage completion on y axis
    # for each module

    result_time = pd.DataFrame(columns=["Date", "Module", "Percentage Completion"])

    for module in modules:
        timestamps = df[df.module_name == module]["completed_at"].dt.date.unique()
        timestamps = [
            x for x in timestamps if type(x) != pd._libs.tslibs.nattype.NaTType
        ]

        for date in timestamps:
            value = round(get_completed_percentage_date(df, module, date) * 100, 1)

            new_df = pd.DataFrame(
                [[date, module, value]],
                columns=["Date", "Module", "Percentage Completion"],
            )

            result_time = pd.concat([result_time, new_df], ignore_index=True)

    # Plotting
    fig_2 = go.Figure()
    for module, group in result_time.groupby("Module"):
        sorted_group = group.sort_values("Date")

        if len(sorted_group) == 1:
            fig_2.add_trace(
                go.Scatter(
                    x=sorted_group["Date"],
                    y=sorted_group["Percentage Completion"],
                    mode="markers",
                    name=module,
                )
            )

        else:
            fig_2.add_trace(
                go.Scatter(
                    x=sorted_group["Date"],
                    y=sorted_group["Percentage Completion"],
                    mode="lines",
                    name=module,
                )
            )

    fig_2.update_layout(
        title="Percentage Completion by Module",
        xaxis=dict(title="Date"),
        yaxis=dict(title="Percentage"),
    )

    # Set custom start and end dates for the x-axis
    start_date = "2019-06-20"
    end_date = "2019-07-20"
    fig_2.update_xaxes(range=[start_date, end_date])

    # Specify custom spacing between dates on the x-axis
    date_spacing = "D7"  # Weekly spacing, adjust as per your requirement
    fig_2.update_xaxes(dtick=date_spacing)

    # Convert the figure to a JSON serializable format
    fig_2_json = fig_2.to_dict()

    return fig_2_json


def item_completion_barplot(df):
    """
    Return a horizontal barplot showing the percentage completion
    of each item under each module

    Inputs:
    --------------


    Returns:
    --------------
    """
    # result dataframe
    student_completion_per_item = pd.DataFrame(
        columns=["Module", "Item", "Item Percentage Completion", "Item Position"]
    )

    # Computing the percentage completion in each item of a module
    for module in modules:
        # number of student id related to Module
        # CHANGE THE NAME TO ID
        df_module = df[(df.module_name == module)]

        for i, item in enumerate(item_dict.get(module)):
            df_module_item = df_module[df_module.items_title == item]

            item_percent_completion = round(
                (
                    df_module_item[df_module_item["item_cp_req_completed"] == True][
                        "student_id"
                    ]
                    .unique()
                    .size
                )
                * 100
                / total_students,
                0,
            )
            new_df = pd.DataFrame(
                [[module, item, item_percent_completion, i + 1]],
                columns=[
                    "Module",
                    "Item",
                    "Item Percentage Completion",
                    "Item Position",
                ],
            )

            student_completion_per_item = pd.concat(
                [student_completion_per_item, new_df], ignore_index=True
            )

    # Plotting
    # Group the DataFrame by 'module'
    grouped_df = student_completion_per_item.groupby("Module")

    # Create subplots with one subplot per module
    fig_3 = make_subplots(
        rows=len(grouped_df), cols=1, shared_xaxes=True, vertical_spacing=0.01
    )

    # Define custom colors for the bars
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]

    # Iterate over each module group
    for i, (module, group) in enumerate(grouped_df):
        # Commenting out since the items should not be sorted
        # Items need to appear in the same order as in the module
        # sorted_group = group.sort_values('Item Percentage Completion', ascending=True)

        # Create a horizontal bar chart for the module
        fig_3.add_trace(
            go.Bar(
                y=group["Item"][::-1],
                x=group["Item Percentage Completion"][::-1],
                orientation="h",
                name=module,
                marker=dict(opacity=0.8),
                text=group["Item Position"][::-1],
                hovertemplate="Item Position: %{text}<br>Item Title: %{y}<br>Completion:%{x}%<extra></extra>",
            ),
            row=i + 1,
            col=1,
        )

    # Update the layout of the figure
    fig_3.update_layout(
        height=150 * len(grouped_df),
        title="Percentage Completion by Item for Each Module",
        xaxis_title="Percentage Completion",
        yaxis_title="Item",
    )

    # Convert the figure to a JSON serializable format
    fig_3_json = fig_3.to_dict()

    return fig_3_json


# -----------------------------------------------------------------------
# Define the layout of the dashboard


# Define the style for the tabs
tab_style = {
    "height": "30px",
    "padding": "8px",
}

# Define the style for the selected tab
selected_tab_style = {
    "height": "30px",
    "padding": "3px",
    "borderTop": "2px solid #f5f5f5",
    "borderBottom": "2px solid #f5f5f5",
    "backgroundColor": "#119DFF",
    "color": "white",
}

# dropdpown options
module_options = [
    {"label": "Course Introduction", "value": "Course Introduction"},
    {"label": "How to Design Data", "value": "How to Design Data"},
    {"label": "How to Design Functions", "value": "How to Design Functions"},
    {"label": "Intro to Object Orientation", "value": "Intro to Object Orientation"},
]

# replace the figure dictionary with the function call for plotly figure plotting
# sidebar = html.Div(
#     [
#         dbc.Row(
#             [
#                 html.P('Filters')
#                 ],
#             style={"height": "5vh"}
#             ),
#         dbc.Row(
#             [
#                 html.P('Select the Module')
#                 ],
#             style={"height": "50vh"}
#             ),
#         dbc.Row(
#             [
#                 html.P('Select the Student')
#                 ],
#             style={"height": "45vh"}
#             )
#         ]
#     )

# content = html.Div(
#     [
#         dbc.Row(
#             [
#                 dbc.Col(
#                      dcc.Graph(id="plot1", figure=module_completion_barplot(data)),
#                      width={"size": 5, "offset": 1, "order": 1},
#                      lg={"size": 5, "offset": 1, "order": 1},
#                  ),
#                 dbc.Col(
#                      dcc.Graph(id="plot2", figure=module_completion_lineplot(data)),
#                      width={"size": 5, "offset": 1, "order": 2},
#                      lg={"size": 5, "offset": 1, "order": 1},
#                  )
#             ],
#             style={"height": "50vh"}),
#         dbc.Row(
#             [
#                 dbc.Col(
#                      dcc.Graph(id="plot3", figure=item_completion_barplot(data)),
#                      width={"size": 6, "offset": 3, "order": 1},
#                      lg={"size": 8, "offset": 2, "order": 1},
#                  )
#             ],
#             style={"height": "50vh"}
#             )
#         ]
#     )


app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.H2(
                    "Module Progress Demo Dashboard",
                    style={
                        "color": "white",
                        "background-color": "black",
                        "padding": "5px",
                    },
                ),
            ],
            style={"padding": "0.05px"},
        ),
        html.Div(
            children=[
                dcc.Tabs(
                    id="tabs",
                    value="Modules",
                    children=[
                        dcc.Tab(
                            label="About",
                            style=tab_style,
                            selected_style=selected_tab_style,
                            children=[
                                html.H1("About"),
                                html.P(
                                    """This is a Sample Dashboard created using Dash and Plotly in Python"""
                                ),
                            ],
                        ),
                        dcc.Tab(
                            label="Module Details",
                            value="Module Details",
                            style=tab_style,
                            selected_style=selected_tab_style,
                            children=[
                                html.Div(
                                    children=[
                                        html.Label(
                                            "Select a module to view the student progression details ",
                                            style={
                                                "font-weight": "bold",
                                                "margin-right": "10px",
                                            },
                                        ),
                                        dcc.Dropdown(
                                            id="module-dropdown",
                                            options=module_options,
                                            value=module_options[0]["value"],
                                            style={"width": "150px", "fontsize": "1px"},
                                        ),
                                    ],
                                    style={
                                        "display": "flex",
                                        "align-items": "center",
                                        "margin-top": "10px",
                                        "margin-bottom": "10px",
                                    },
                                ),
                                html.Div(
                                    children=[
                                        dcc.Graph(
                                            id="plot1",
                                            figure=module_completion_barplot(data),
                                            style={
                                                "width": "50%",
                                                "height": "500px",
                                                "display": "inline-block",
                                                "border": "2px solid #ccc",
                                                "border-radius": "5px",
                                                "padding": "10px",
                                            },
                                        ),
                                        dcc.Graph(
                                            id="plot3",
                                            figure=item_completion_barplot(data),
                                            style={
                                                "width": "50%",
                                                "height": "500px",
                                                "display": "inline-block",
                                                "border": "2px solid #ccc",
                                                "border-radius": "5px",
                                                "padding": "10px",
                                            },
                                        ),
                                        # dcc.Graph(id='ratio-graph', style={'width': '50%', 'display': 'inline-block'})
                                    ]
                                ),
                            ],
                        ),
                        dcc.Tab(
                            label="Progress Lineplot",
                            style=tab_style,
                            selected_style=selected_tab_style,
                            children=[
                                html.H1("Date  filters to be added"),
                                dcc.Graph(
                                    id="plot2", figure=module_completion_lineplot(data)
                                ),
                            ],
                        ),
                    ],
                )
            ],
            style={
                "padding": "20px",
                "background-color": "#F8F8FF",
                "fontSize": "16px",
            },
        ),
    ]
)


# app.layout = dbc.Container(
#     [
#         dbc.Row(
#             [
#                 dbc.Col(sidebar, width=3, className='bg-light'),
#                 dbc.Col(content, width=9)
#                 ]
#             ),
#         ],
#     fluid=True
#     )


# app.layout = dbc.Container(
#     fluid=True,
#     children=[
#         html.H1(
#             "Module Progress Dashboard",
#             className="display-4",
#         ),
#         dbc.Row(
#             [
#                 dbc.Col(
#                     dcc.Graph(id="plot1", figure=module_completion_barplot(data)),
#                     width={"size": 5, "offset": 1, "order": 1},
#                     lg={"size": 5, "offset": 1, "order": 1},
#                 ),
#                 dbc.Col(
#                     dcc.Graph(id="plot2", figure=module_completion_lineplot(data)),
#                     width={"size": 5, "offset": 1, "order": 2},
#                     lg={"size": 5, "offset": 1, "order": 1},
#                 ),
#             ],
#             className="mt-4",
#         ),
#         dbc.Row(
#             [
#                 dbc.Col(
#                     dcc.Graph(id="plot3", figure=item_completion_barplot(data)),
#                     width={"size": 6, "offset": 3, "order": 1},
#                     lg={"size": 8, "offset": 2, "order": 1},
#                 )
#             ],
#             className="mt-4",
#         ),
#     ],
# )

if __name__ == "__main__":
    app.run_server(debug=True)
