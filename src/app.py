# imports
from dash import dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc
import dash
from dash.dependencies import Input, Output, State
import re

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
# Global variables
# CHANGE TO MODULE ID INSTEAD OF NAME
modules = list(data.module_id.unique())
total_students = data.student_id.unique().size

# Make a dictionary of module id and module names
module_dict, item_dict, course_dict, student_dict = (defaultdict(str) for _ in range(4))

for _, row in data.iterrows():
    module_dict[str(row["module_id"])] = re.sub(
        r"^Module\s+\d+:\s+", "", row["module_name"]
    )
    item_dict[str(row["items_module_id"])] = row["items_title"]
    course_dict[str(row["course_id"])] = row["course_name"]
    student_dict[str(row["student_id"])] = row["student_name"]

# Creating a dictionary of items per module
items_in_module = defaultdict(str)

for module in module_dict.keys():
    items_in_module[str(module)] = list(
        data[data.module_id.astype(str) == module].items_title.unique()
    )


# -------------------------------------------------------------
# Helper Functions
def get_completed_percentage(df, module, state="completed"):
    """
    Returns the state percentage of module in df

    Input:
    ---------


    Returns:
    ---------
    """
    df_module = df[df.module_id.astype(str) == module]

    # df is a subset dataframe that contains a specific module as selected in the dropdown
    # Thus when other modules are iterated the size of the dataframe will be 0

    if df_module.shape[0] == 0:
        return 0

    total_module_students = df_module.student_id.unique().size
    percentage = (
        df_module[df_module.state == state].student_id.unique().size
        / total_module_students
    )
    return percentage


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
    df_module = df[df.module_id.astype(str) == module]
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


# ------------------------------------------------------
# Plotting Functions


def module_completion_barplot(df):
    """
    Plots a horizontal barplot of student percentage module completion per module

    Input:
    -----------


    Returns:
    -----------

    """
    result = {}
    modules = list(df.module_id.unique().astype(str))

    for module in modules:
        result[module_dict.get(module)] = [
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

    # Define the color mapping
    color_mapping = {
        "unlocked": "#cafb9c",
        "started": "#77bc34",
        "completed": "#0d203e",
    }

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
        color_discrete_map=color_mapping,  # Set the color mapping
    )

    fig_1.update_layout(
        showlegend=True,  # Show the legend indicating the module status colors
        legend_title="Status",  # Customize the legend title,
        legend_traceorder="reversed",  # Reverse the order of the legend items
    )

    # Modify the plotly configuration to change the background color
    fig_1.update_layout(
        plot_bgcolor="rgb(255, 255, 255)"  # Set the desired background color
    )

    # Convert the figure to a JSON serializable format
    fig_1_json = fig_1.to_dict()

    return fig_1_json


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

    for module in module_dict.keys():
        timestamps = df[df.module_id.astype(str) == module][
            "completed_at"
        ].dt.date.unique()
        timestamps = [
            x for x in timestamps if type(x) != pd._libs.tslibs.nattype.NaTType
        ]

        for date in timestamps:
            value = round(get_completed_percentage_date(df, module, date) * 100, 1)

            new_df = pd.DataFrame(
                [[date, module_dict.get(module), value]],
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
    modules = list(df.module_id.unique().astype(str))

    for module in modules:
        # number of student id related to Module
        # CHANGE THE NAME TO ID
        df_module = df[(df.module_id.astype(str) == module)]

        for i, item in enumerate(items_in_module.get(module)):
            df_module_item = df_module[df_module.items_title.astype(str) == item]

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
                [[module_dict.get(module), item, item_percent_completion, i + 1]],
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
                text=[],
                hovertemplate="Item Title: %{y}<br>Completion:%{x}%<extra></extra>",
            ),
            row=i + 1,
            col=1,
        )

    # Update the layout of the figure
    fig_3.update_layout(
        height=300 * len(grouped_df),
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
    {"label": module_name, "value": module_id}
    for module_id, module_name in module_dict.items()
]
module_options.extend([{"label": "All", "value": "All"}])


# ----------------------------
# Define callbacks


@app.callback(
    Output("plot1", "figure"),
    [Input("module-dropdown", "value")],
)
def update_module(val):
    subset_data = data.copy()
    # if a specific module is selected then filter the dataframe by that alone, else select all.
    if val != "All":
        subset_data = data[data.module_id.astype(str) == val]

    fig = module_completion_barplot(subset_data)
    return fig


@app.callback(
    Output("plot3", "figure"),
    [Input("module-dropdown", "value")],
)
def update_items(val):
    subset_data = data.copy()
    # if a specific module is selected then filter the items that belong to that module alone, else seletc all
    if val != "All":
        subset_data = data[data.module_id.astype(str) == val]

    fig = item_completion_barplot(subset_data)
    return fig


# Need to move this to Callback, Define the start and end dates
start_date = "2019-06-20"
end_date = "2019-07-20"
# ----------------------------


app.layout = dbc.Container(
    fluid=True,
    children=[
        html.Div(
            children=[
                html.H2(
                    "Module Progress Demo Dashboard",
                    style={
                        "color": "white",
                        "background-color": "black",
                        "padding": "5px",
                        "text-align": "center",
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
                                html.Div(
                                    className="about-container",
                                    children=[
                                        html.H1("About"),
                                        html.P(
                                            """This Sample Dashboard is created using Dash and Plotly in Python. It provides an interactive visualization of student progression in different modules. The dashboard allows you to explore module details, view student progress through completion bar plots, and analyze overall module completion using a line plot. With an intuitive interface and visually appealing design, this dashboard offers a comprehensive overview of student progress and module completion. It is a powerful tool for educators and administrators to track and monitor student performance in an easy-to-understand manner."""
                                        ),
                                    ],
                                )
                            ],
                        ),
                        dcc.Tab(
                            label="Module Details",
                            value="Module Details",
                            style=tab_style,
                            selected_style=selected_tab_style,
                            children=[
                                html.Div(
                                    className="module-dropdown-container",
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
                                            value=module_options[-1]["value"],
                                            style={"width": "300px", "fontsize": "1px"},
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
                                    className="plot-container",
                                    children=[
                                        html.Div(
                                            className="first-row",
                                            children=[
                                                dcc.Graph(
                                                    id="plot1",
                                                    style={
                                                        "width": "100%",
                                                        "height": "400px",
                                                        "display": "inline-block",
                                                        "border": "2px solid #ccc",
                                                        "border-radius": "5px",
                                                        "padding": "10px",
                                                    },
                                                ),
                                            ],
                                            style={
                                                "display": "flex",
                                                "justify-content": "space-between",
                                            },
                                        ),
                                        html.Div(
                                            className="second-row",
                                            children=[
                                                dcc.Graph(
                                                    id="plot3",
                                                    figure=item_completion_barplot(
                                                        data
                                                    ),
                                                    style={
                                                        "width": "100%",
                                                        "height": "400px",
                                                        "display": "inline-block",
                                                        "border": "2px solid #ccc",
                                                        "border-radius": "5px",
                                                        "padding": "10px",
                                                    },
                                                ),
                                            ],
                                            style={
                                                "display": "flex",
                                                "justify-content": "space-between",
                                            },
                                        ),
                                    ],
                                ),
                            ],
                        ),
                        dcc.Tab(
                            label="Progress Lineplot",
                            style=tab_style,
                            selected_style=selected_tab_style,
                            children=[
                                html.H2("Select the Date Range"),
                                dcc.RangeSlider(
                                    id="date-slider",
                                    min=0,
                                    max=100,
                                    step=1,
                                    value=[0, 100],
                                    marks={0: start_date, 100: end_date},
                                ),
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
    ],
)


if __name__ == "__main__":
    app.run_server(debug=True)
