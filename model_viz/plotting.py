import plotly.graph_objects as go
import numpy as np

# TODO: Add a ConfigParser to read in config file


class BasePlotter:
    name = "BasePlotter"

    def __init__(self):
        self.data = None
        self.empirical_data = None

    def create_plot(self, **kwargs):
        raise NotImplementedError


class Histogram2D(BasePlotter):
    name = "Histogram2D"

    def __init__(self, data: np.ndarray, empirical_data=None):
        super().__init__()
        self.data = data
        self.empirical_data = empirical_data

    def create_plot(self, **kwargs):
        """Create 2D histogram plot from samples and overlay empirical data if provided.

        Returns:
            go.Figure: Plotly figure
        """
        x = np.tile(np.arange(self.data.shape[1]), self.data.shape[0])
        y = self.data.flatten()
        title = kwargs.get("title", "Histogram2D")
        x_title = kwargs.get("x_title", "Time")
        y_title = kwargs.get("y_title", "Value")

        fig = go.Figure(
            go.Histogram2d(
                x=x,
                y=y,
                colorbar=dict(title="Count", titleside="right"),
                histfunc="count",
            )
        ).update_layout(
            title=title,
            xaxis_title=x_title,
            yaxis_title=y_title,
        )

        if self.empirical_data is not None:
            fig.add_trace(
                go.Scatter(
                    x=np.arange(self.empirical_data.shape[0]),
                    y=self.empirical_data,
                    mode="markers",
                )
            )

        return fig


class BoxPlotOverTime(BasePlotter):
    name = "BoxPlotOverTime"

    def __init__(self, data: np.ndarray, empirical_data=None):
        super().__init__()
        self.data = data
        self.empirical_data = empirical_data

    def create_plot(self, **kwargs):
        """Create a box plot over time overlayed with empirical data if provided.

        Returns:
            go.Figure: Plotly figure
        """

        title = kwargs.get("title", "BoxPlotOverTime")
        x_title = kwargs.get("x_title", "Time")
        y_title = kwargs.get("y_title", "Value")

        fig = go.Figure(
            go.Box(
                x=np.tile(np.arange(self.data.shape[1]), self.data.shape[0]),
                y=self.data.flatten(),
                boxpoints=False,
                showlegend=False,
            )
        ).update_layout(
            title=title,
            xaxis_title=x_title,
            yaxis_title=y_title,
        )

        if self.empirical_data is not None:
            fig.add_trace(
                go.Scatter(
                    x=np.arange(self.empirical_data.shape[0]),
                    y=self.empirical_data,
                    mode="markers",
                    showlegend=False,
                )
            )

        return fig
