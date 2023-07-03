import plotly.graph_objects as go
import numpy as np


class BasePlotter:
    name = "BasePlotter"

    def __init__(self):
        self.data = None
        self.empirical_data = None

    def create_plot(self, stock):
        raise NotImplementedError


class Histogram2D(BasePlotter):
    name = "Histogram2D"

    def __init__(self, data, empirical_data=None):
        super().__init__()
        self.data = data
        self.empirical_data = empirical_data

    def create_plot(self):
        x = np.arange(self.data.shape[0])
        y = self.data
        return go.Histogram2d(
            x=x,
            y=y,
            nbinsx=x.shape[0],
        )
