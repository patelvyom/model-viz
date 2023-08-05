import sys
import h5py
import model_viz.config as config
import model_viz.utils as utils
import model_viz.hdf_ops as hdf_ops
import model_viz.plotting as plotting
import model_viz.component_factory as component_factory
import dash
from dash import html, dcc, Input, Output, State, MATCH
import plotly.graph_objects as go
import functools
import dash_bootstrap_components as dbc
from typing import List

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.PULSE])

GRAPH_TYPES = {
    "Histogram 2D": plotting.Histogram2D,
    "Boxplot over Time": plotting.BoxPlotOverTime,
}


def generate_plots(
    groups: list[h5py.Group], graph_type: str
) -> List[plotting.BasePlotter]:
    """Generate plots from HDF5 file and return list of plots

    Args:
        groups: List of HDF5 groups
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
    for plot_item in groups:
        title = plot_item.name.split("/")[-1]
        data = plot_item["data"][:]
        overlay_data = (
            plot_item["overlay_data"][:].flatten()
            if "overlay_data" in plot_item
            else None
        )
        plot = plotter(data=data, overlay_data=overlay_data)
        plot.create_plot(title=title)
        plots.append(plot)

    return plots


def main(argv):
    reader = hdf_ops.HDFReader("reader", argv[0])
    groups_to_plot = reader.get_groups()
    group_tabs = {
        group: component_factory.DashTab(label=group, component_id=group)
        for group in groups_to_plot.keys()
    }
    dash_tabs = component_factory.DashTabs(
        component_id="dash_tabs", tabs=list(group_tabs.values())
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
                    dcc.Download(id="download"),
                    html.Br(),
                    html.Div(dash_tabs),
                    html.Div(
                        [
                            html.Div(
                                id="tab_content_1",
                                style={"width": "75%", "display": "inline-block"},
                            ),
                            html.Div(
                                id="tab_content_2",
                                style={"width": "25%", "display": "inline-block"},
                            ),
                        ]
                    ),
                ]
            )
        ],
        fluid=True,
    )

    @app.callback(
        Output("tab_content_1", "children"),
        Output("tab_content_2", "children"),
        Input("graph_type", "value"),
        Input("dash_tabs", "active_tab"),
    )
    @functools.lru_cache(maxsize=32)
    def update_graph1(graph_type, active_tab):
        if graph_type is not None:
            if active_tab in group_tabs:
                dash_graphs_1 = []
                dash_graphs_2 = []
                for plot in generate_plots(groups_to_plot[active_tab], graph_type):
                    dash_graphs_1.append(
                        dcc.Graph(
                            id={"type": "dcc_go_1", "index": plot.title},
                            figure=plot.fig,
                            style=config.Plotter.graph_div_style,
                        )
                    )
                    dash_graphs_2.append(
                        dcc.Graph(
                            id={
                                "type": "dcc_go_2",
                                "index": plot.title,
                            },  # Create empty fig
                            style=config.Plotter.graph_div_style,
                        )
                    )
                return dash_graphs_1, dash_graphs_2
            else:
                raise NotImplementedError(f"Active tab {active_tab} not implemented")

        return dash.no_update

    @app.callback(
        Output({"type": "dcc_go_2", "index": MATCH}, "figure"),
        Input({"type": "dcc_go_1", "index": MATCH}, "hoverData"),
        State({"type": "dcc_go_1", "index": MATCH}, "id"),
        State("dash_tabs", "active_tab"),
        prevent_initial_call=True,
    )
    def update_graph2(hover_data, id, active_tab):
        graph_title = id["index"]
        x = int(hover_data["points"][0]["x"])
        data_x = reader[f"{active_tab}/{graph_title}"]["data"][
            :, x
        ]  # Get data for time step x
        # TODO: Make this a function in plotting.py. Make orientation configurable.

        return go.Figure(go.Histogram(y=data_x)).update_layout(
            xaxis_title="Count", yaxis_title="Value"
        )

    @app.callback(
        Output("export", "n_clicks"),
        Output("download", "data"),
        Input("graph_type", "value"),
        Input("export", "n_clicks"),
        prevent_initial_call=True,
    )
    def export_plots(graph_type, n_clicks):
        if graph_type is not None and n_clicks is not None:
            files = []
            for group in groups_to_plot.values():
                files += [
                    plot.export_plot() for plot in generate_plots(group, graph_type)
                ]
            utils.merge_pdf_files(files, config.output_filename)
            return None, dcc.send_file(config.output_filename)

        return dash.no_update

    app.run_server(debug=True)


if __name__ == "__main__":
    main(sys.argv[1:])
