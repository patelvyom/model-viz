import sys
import model_viz
import dash
from dash import Dash, html, dcc, Input, Output

app = dash.Dash(__name__)


def main(argv):
    reader = model_viz.hdf_ops.HDFReader("reader", argv[0])
    stocks = reader.get_iterator("stocks_with_empirical_data")
    figs = []
    for stock in stocks:
        title = stock.name.split("/")[-1]
        data = stock["model_values"][:]
        empirical_data = (
            stock["empirical_values"][:].flatten()
            if "empirical_values" in stock
            else None
        )
        plotter = model_viz.plotting.Histogram2D(data, empirical_data=empirical_data)
        fig = plotter.create_plot(title=title, x_title="Time", y_title="Value")
        figs.append(html.Div([dcc.Graph(figure=fig)]))

    app.layout = html.Div([html.H1("Model-Viz")] + figs)
    app.run_server(debug=True)


if __name__ == "__main__":
    main(sys.argv[1:])
