import sys
import h5py
import model_viz.config as config
import model_viz.utils as utils
import model_viz.hdf_ops as hdf_ops
import model_viz.plotting as plotting
import model_viz.component_factory as component_factory
import dash
from dash import html, dcc, Input, Output
from itertools import chain
import functools
import dash_bootstrap_components as dbc
from typing import List, Iterator

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.PULSE])

GRAPH_TYPES = {
    "Histogram 2D": plotting.Histogram2D,
    "Boxplot over Time": plotting.BoxPlotOverTime,
}


def generate_plots(
    groups: Iterator[h5py.Group], graph_type: str
) -> List[plotting.BasePlotter]:
    """Generate plots from HDF5 file and return list of plots

    Args:
        groups: Iterator of HDF5 groups
        graph_type (str): Type of graph to generate

    Raises:
        NotImplementedError: If graph type is not implemented

    Returns:
        list: List of plots where each plot is a Plotly figure
    """
    if graph_type not in GRAPH_TYPES:
        raise NotImplementedError(f"Graph type {graph_type} not implemented")

    plots = []
    plotter = GRAPH_TYPES[graph_type]
    for plotting_group in groups:
        title = plotting_group.name.split("/")[-1]
        data = plotting_group["model_values"][:]
        empirical_data = (
            plotting_group["empirical_values"][:].flatten()
            if "empirical_values" in plotting_group
            else None
        )
        plot = plotter(data=data, empirical_data=empirical_data)
        plot.create_plot(title=title)
        plots.append(plot)

    return plots


def main(argv):
    reader = hdf_ops.HDFReader("reader", argv[0])
    plotting_groups = reader.get_groups()
    group_tabs = {
        group: component_factory.DashTab(label=group, component_id=group)
        for group in plotting_groups.keys()
    }
    dash_tabs = component_factory.DashTabs(
        component_id="group_tabs", tabs=list(group_tabs.values())
    ).generate_component()

    app.layout = dbc.Container(
        [
            html.Div(
                [
                    html.Br(),
                    html.H1("Model-Viz"),
                    html.Hr(),
                    dcc.Dropdown(
                        options=list(GRAPH_TYPES.keys()),
                        placeholder="Select Graph Type",
                        id="graph_type",
                    ),
                    html.Br(),
                    dbc.Spinner(
                        dbc.Button(
                            "Export All Plots",
                            color="primary",
                            id="export",
                            class_name="me-1",
                        )
                    ),
                    html.Br(),
                    html.Div([dash_tabs, dbc.Spinner(html.Div(id="tab_content"))]),
                ]
            )
        ],
        fluid=True,
    )

    @app.callback(
        Output("tab_content", "children"),
        Input("graph_type", "value"),
        Input("group_tabs", "active_tab"),
    )
    @functools.lru_cache(maxsize=32)
    def update_graph(graph_type, active_tab):
        if graph_type is not None:
            if active_tab in group_tabs:
                return [
                    dcc.Graph(figure=plot.fig, style=config.Plotter.graph_div_style)
                    for plot in generate_plots(plotting_groups[active_tab], graph_type)
                ]
            else:
                raise NotImplementedError(f"Active tab {active_tab} not implemented")

    @app.callback(
        Output("export", "n_clicks"),
        Input("graph_type", "value"),
        Input("export", "n_clicks"),
    )
    def export_plots(graph_type, n_clicks):
        if graph_type is not None and n_clicks is not None:
            iterator = chain(
                # get_iterator(argv[0], "stocks_with_empirical_data"),
                # get_iterator(argv[0], "stocks"),
            )
            files = [
                plot.export_plot() for plot in generate_plots(iterator, graph_type)
            ]
            utils.merge_pdf_files(files, config.output_filename)

    app.run_server(debug=True)


if __name__ == "__main__":
    main(sys.argv[1:])
