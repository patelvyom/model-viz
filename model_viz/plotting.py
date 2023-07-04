import plotly.graph_objects as go
import numpy as np
import pandas as pd


class BasePlotter:
    name = "BasePlotter"

    def __init__(self):
        self.data = None
        self.empirical_data = None

    def create_plot(self, stock):
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

        return go.Figure(
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
