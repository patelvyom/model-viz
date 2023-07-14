import sys
import model_viz
import dash
from dash import Dash, html, dcc, Input, Output
from itertools import chain
import functools

graph_types = [
    {"label": "2D-Histogram", "value": "2d_hist"},
    {"label": "Boxplot over Time", "value": "boxplot_over_time"},
]
app = dash.Dash(__name__)


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
    app.layout = html.Div(
        [
            html.H1("Model-Viz"),
            dcc.Dropdown(
                options=graph_types, placeholder="Select Graph Type", id="graph_type"
            ),
            html.Button("Export", id="export"),
            html.Div(id="figures"),
        ]
    )

    @app.callback(Output("figures", "children"), Input("graph_type", "value"))
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
            [plot.export_plot() for plot in generate_plots(argv[0], graph_type)]

    app.run_server(debug=True)


if __name__ == "__main__":
    main(sys.argv[1:])
