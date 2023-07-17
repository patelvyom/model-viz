import sys
import os
import model_viz
import model_viz.config as config
import dash
from dash import Dash, html, dcc, Input, Output
from itertools import chain
import functools
import dash_bootstrap_components as dbc
from PyPDF2 import PdfMerger
from datetime import datetime
from typing import List, Iterator
import numpy as np

graph_types = [
    {"label": "2D-Histogram", "value": "2d_hist"},
    {"label": "Boxplot over Time", "value": "boxplot_over_time"},
]
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.PULSE])


def merge_pdf_files(files: List[str], output_file: str) -> None:
    """Merge multiple PDF files into one PDF file

    Args:
        files (list): List of PDF files to merge
        output_file (str): Output file name
    """

    merger = PdfMerger()
    for file in files:
        merger.append(file)
    merger.write(output_file)
    merger.close()


def get_iterator(hdf_path: str, group: str) -> Iterator[np.ndarray]:
    """Returns iterator for HDF5 group

    Args:
        hdf_path (str): Path to HDF5 file
        group (str): Group name

    Returns:
        model_viz.hdf_ops.HDFReader: Iterator for HDF5 group
    """
    reader = model_viz.hdf_ops.HDFReader("reader", hdf_path)
    return reader.get_iterator(group)


def generate_plots(
    iterator: Iterator[np.ndarray], graph_type: str
) -> List[model_viz.plotting.BasePlotter]:
    """Generate plots from HDF5 file and return list of plots

    Args:
        hdf_path (str): Path to HDF5 file
        graph_type (str): Type of graph to generate

    Raises:
        NotImplementedError: If graph type is not implemented

    Returns:
        list: List of plots where each plot is a Plotly figure
    """
    print("[main.py] Generating plots")
    plots = []
    if graph_type == "2d_hist":
        plotter = model_viz.plotting.Histogram2D
    elif graph_type == "boxplot_over_time":
        plotter = model_viz.plotting.BoxPlotOverTime
    else:
        raise NotImplementedError(f"Graph type {graph_type} not implemented")

    for stock in iterator:
        title = stock.name.split("/")[-1]
        data = stock["model_values"][:]
        empirical_data = (
            stock["empirical_values"][:].flatten()
            if "empirical_values" in stock
            else None
        )
        plot = plotter(data=data, empirical_data=empirical_data)
        plot.create_plot(title=title)
        plots.append(plot)

    return plots


def main(argv):
    tabs = html.Div(
        [
            dbc.Tabs(
                [
                    dbc.Tab(
                        label="Stocks with Empirical Data",
                        tab_id="stocks_with_empirical_data",
                    ),
                    dbc.Tab(label="Stocks", tab_id="stocks"),
                ],
                id="tabs",
                active_tab="stocks_with_empirical_data",
            ),
            dbc.Spinner(html.Div(id="tab_content")),
        ]
    )

    app.layout = dbc.Container(
        [
            html.Div(
                [
                    html.Br(),
                    html.H1("Model-Viz"),
                    html.Hr(),
                    dcc.Dropdown(
                        options=graph_types,
                        placeholder="Select Graph Type",
                        id="graph_type",
                    ),
                    html.Br(),
                    dbc.Spinner(
                        dbc.Button(
                            "Export Plots",
                            color="primary",
                            id="export",
                            class_name="me-1",
                        )
                    ),
                    tabs,
                ]
            )
        ],
        fluid=True,
    )

    @app.callback(
        Output("tab_content", "children"),
        Input("graph_type", "value"),
        Input("tabs", "active_tab"),
    )
    @functools.lru_cache(maxsize=32)
    def update_graph(graph_type, active_tab):
        if graph_type is not None:
            if active_tab == "stocks_with_empirical_data":
                iterator = get_iterator(argv[0], "stocks_with_empirical_data")
            elif active_tab == "stocks":
                iterator = get_iterator(argv[0], "stocks")
            else:
                raise NotImplementedError(f"Active tab {active_tab} not implemented")
            return [
                dcc.Graph(figure=plot.fig)
                for plot in generate_plots(iterator, graph_type)
            ]

    @app.callback(
        Output("export", "n_clicks"),
        Input("graph_type", "value"),
        Input("export", "n_clicks"),
    )
    def export_plots(graph_type, n_clicks):
        if graph_type is not None and n_clicks is not None:
            iterator = chain(
                get_iterator(argv[0], "stocks_with_empirical_data"),
                get_iterator(argv[0], "stocks"),
            )
            files = [
                plot.export_plot() for plot in generate_plots(iterator, graph_type)
            ]
            merge_pdf_files(files, config.output_filename)

    app.run_server(debug=True)


if __name__ == "__main__":
    main(sys.argv[1:])
