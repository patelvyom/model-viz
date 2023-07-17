import plotly.graph_objects as go
import numpy as np
import os
import model_viz.config as config
import datashader as ds
import pandas as pd
import plotly.express as px


class BasePlotter:
    name: str = "BasePlotter"
    fig = None
    title = None

    def __init__(self):
        self.data = None
        self.empirical_data = None

    def create_plot(self, **kwargs):
        raise NotImplementedError

    def export_plot(self) -> str:
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

    def create_plot(self, **kwargs) -> go.Figure:
        """Create 2D histogram plot from samples and overlay empirical data if provided.

        Returns:
            go.Figure: Plotly figure
        """
        self.title = kwargs.get("title", config.Histogram2D.title)
        x_title = kwargs.get("x_title", config.Histogram2D.x_title)
        y_title = kwargs.get("y_title", config.Histogram2D.y_title)
        x = np.tile(np.arange(self.data.shape[1]), self.data.shape[0])
        y = self.data.flatten()
        df = pd.DataFrame({"x": x, "y": y})

        # Rasterising Hist2D for faster rendering. See https://plotly.com/python/datashader/
        cvs = ds.Canvas(plot_height=100, plot_width=100)
        agg = cvs.points(df, "x", "y", ds.count())
        zero_mask = agg.values == 0
        agg.values = np.log10(agg.values, where=np.logical_not(zero_mask))
        agg.values[zero_mask] = np.nan

        fig = px.imshow(
            agg,
            origin="lower",
            labels={"color": f"Log10({config.Histogram2D.colorbar_title})"},
        )
        fig.update_layout(
            coloraxis_colorbar={
                "title": config.Histogram2D.colorbar_title,
                "tickprefix": "1.e",
            },
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
                    marker_color=config.Histogram2D.scatter_color,
                    name="Empirical Data",
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

    def create_plot(self, **kwargs) -> go.Figure:
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
                    name="Empirical Data",
                    marker_color=config.BoxPlotOverTime.scatter_color,
                )
            )
        self.fig = fig
        return fig
