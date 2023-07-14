import sys
import os
import model_viz
import dash
from dash import Dash, html, dcc, Input, Output
from itertools import chain
import functools
import dash_bootstrap_components as dbc
from PyPDF2 import PdfMerger
from datetime import datetime

graph_types = [
    {"label": "2D-Histogram", "value": "2d_hist"},
    {"label": "Boxplot over Time", "value": "boxplot_over_time"},
]
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.PULSE])


def merge_pdf_files(files, output_file):
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


def generate_plots(hdf_path, graph_type):
    reader = model_viz.hdf_ops.HDFReader("reader", hdf_path)
    stocks = reader.get_iterator("stocks")
    stocks_with_empirical_data = reader.get_iterator("stocks_with_empirical_data")
    plots = []
    if graph_type == "2d_hist":
        plotter = model_viz.plotting.Histogram2D
    elif graph_type == "boxplot_over_time":
        plotter = model_viz.plotting.BoxPlotOverTime
    else:
        raise NotImplementedError(f"Graph type {graph_type} not implemented")

    for stock in chain(stocks_with_empirical_data, stocks):
        title = stock.name.split("/")[-1]
        print(f"Creating plot for {title}")
        data = stock["model_values"][:]
        empirical_data = (
            stock["empirical_values"][:].flatten()
            if "empirical_values" in stock
            else None
        )
        plot = plotter(data=data, empirical_data=empirical_data)
        plot.create_plot(title=title, x_title="Time", y_title="Value")
        plots.append(plot)

    return plots


def main(argv):
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
                    dbc.Button(
                        "Export Plots", color="primary", id="export", class_name="me-1"
                    ),
                    html.Div(id="plots"),
                ]
            )
        ],
        fluid=True,
    )

    @app.callback(Output("plots", "children"), Input("graph_type", "value"))
    @functools.lru_cache(maxsize=32)
    def update_graph(graph_type):
        if graph_type is not None:
            return [
                dcc.Graph(figure=plot.fig)
                for plot in generate_plots(argv[0], graph_type)
            ]

    @app.callback(
        Output("export", "n_clicks"),
        Input("graph_type", "value"),
        Input("export", "n_clicks"),
    )
    def export_plots(graph_type, n_clicks):
        if graph_type is not None and n_clicks is not None:
            files = [plot.export_plot() for plot in generate_plots(argv[0], graph_type)]
            merge_pdf_files(
                files, f'output/{datetime.now().strftime("%Y-%m-%d")}_plots.pdf'
            )

    app.run_server(debug=True)


if __name__ == "__main__":
    main(sys.argv[1:])
