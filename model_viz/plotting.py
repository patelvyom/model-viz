import plotly.graph_objects as go
import numpy as np
import os
import model_viz.config as config


class BasePlotter:
    name = "BasePlotter"
    fig = None
    title = None

    def __init__(self):
        self.data = None
        self.empirical_data = None

    def create_plot(self, **kwargs):
        raise NotImplementedError

    def export_plot(self):
        path = os.path.join(
            config.Plotter.output_dir,
            f"{self.title}.{config.Plotter.output_file_format}",
        )
        self.fig.write_image(
            path,
            engine=config.Plotter.export_engine,
            width=config.Plotter.width,
            height=config.Plotter.height,
        )
        return path


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
        self.title = kwargs.get("title", config.Histogram2D.title)
        x_title = kwargs.get("x_title", config.Histogram2D.x_title)
        y_title = kwargs.get("y_title", config.Histogram2D.y_title)
        x = np.tile(np.arange(self.data.shape[1]), self.data.shape[0])
        y = self.data.flatten()

        fig = go.Figure(
            go.Histogram2d(
                x=x,
                y=y,
                colorbar=dict(
                    title=config.Histogram2D.colorbar_title,
                    titleside=config.Histogram2D.colorbar_titleside,
                ),
                histfunc=config.Histogram2D.histfunc,
            )
        ).update_layout(
            title=self.title,
            xaxis_title=x_title,
            yaxis_title=y_title,
        )

        if self.empirical_data is not None:
            fig.add_trace(
                go.Scatter(
                    x=np.arange(self.empirical_data.shape[0]),
                    y=self.empirical_data,
                    mode=config.Histogram2D.scatter_mode,
                )
            )

        self.fig = fig
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

        self.title = kwargs.get("title", config.Histogram2D.title)
        x_title = kwargs.get("x_title", config.Histogram2D.x_title)
        y_title = kwargs.get("y_title", config.Histogram2D.y_title)
        x = np.tile(np.arange(self.data.shape[1]), self.data.shape[0])
        y = self.data.flatten()

        fig = go.Figure(
            go.Box(
                x=x,
                y=y,
                boxpoints=config.BoxPlotOverTime.boxpoints,
                showlegend=config.BoxPlotOverTime.showlegend,
            )
        ).update_layout(
            title=self.title,
            xaxis_title=x_title,
            yaxis_title=y_title,
        )

        if self.empirical_data is not None:
            fig.add_trace(
                go.Scatter(
                    x=np.arange(self.empirical_data.shape[0]),
                    y=self.empirical_data,
                    mode=config.BoxPlotOverTime.scatter_mode,
                    showlegend=config.BoxPlotOverTime.showlegend,
                )
            )
        self.fig = fig
        return fig
