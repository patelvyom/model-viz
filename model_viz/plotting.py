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

    def __init__(self, data=None, overlay_data=None):
        self.data = data
        self.overlay_data = overlay_data

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

    def update_x_ticks(self, x_tick_vals):
        if config.Plotter.is_xlabel_date:
            tick_interval = max(
                1, x_tick_vals.shape[0] // config.Plotter.desired_tick_labels
            )
            x_tick_text = pd.to_datetime(config.Plotter.day_zero) + pd.to_timedelta(
                x_tick_vals, unit="D"
            )
            x_tick_text = x_tick_text.strftime("%Y-%m-%d")
            self.fig.update_xaxes(
                tickangle=-45,
                tickmode="array",
                tickvals=x_tick_vals[::tick_interval],
                ticktext=x_tick_text[::tick_interval],
            )


class Histogram2D(BasePlotter):
    name = "Histogram2D"

    def __init__(self, data: np.ndarray, overlay_data=None):
        super().__init__(data, overlay_data)

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
            color_continuous_scale=config.Histogram2D.colorscale,
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

        if self.overlay_data is not None:
            fig.add_trace(
                go.Scatter(
                    x=np.arange(self.overlay_data.shape[0]),
                    y=self.overlay_data,
                    mode=config.Histogram2D.scatter_mode,
                    marker_color=config.Histogram2D.scatter_color,
                    name=config.Histogram2D.scatter_name,
                )
            )
        self.fig = fig
        self.update_x_ticks(np.arange(self.data.shape[1]))
        return fig


class BoxPlotOverTime(BasePlotter):
    name = "BoxPlotOverTime"

    def __init__(self, data: np.ndarray, overlay_data=None):
        super().__init__(data, overlay_data)

    def _pre_compute_boxplot_stats(self) -> dict[str, np.ndarray]:
        """Compute boxplot aggregation statistics over time.

        Returns:
            np.array: array of computed stats
        """
        stats = np.array(
            [
                np.min(self.data, axis=0),
                np.percentile(self.data, 25, axis=0),
                np.median(self.data, axis=0),
                np.percentile(self.data, 75, axis=0),
                np.max(self.data, axis=0),
            ]
        ).T
        return {
            "lower_fence": stats[:, 0],
            "q1": stats[:, 1],
            "median": stats[:, 2],
            "q3": stats[:, 3],
            "upper_fence": stats[:, 4],
        }

    def create_plot(self, **kwargs) -> go.Figure:
        """Create a box plot over time overlayed with empirical data if provided.

        Returns:
            go.Figure: Plotly figure
        """

        self.title = kwargs.get("title", config.Histogram2D.title)
        x_title = kwargs.get("x_title", config.Histogram2D.x_title)
        y_title = kwargs.get("y_title", config.Histogram2D.y_title)

        # Pre-compute all stats for faster rendering.
        stats = self._pre_compute_boxplot_stats()

        fig = go.Figure(
            go.Box(
                q1=stats["q1"],
                q3=stats["q3"],
                median=stats["median"],
                boxpoints=config.BoxPlotOverTime.boxpoints,
                showlegend=config.BoxPlotOverTime.showlegend,
            )
        ).update_layout(title=self.title, xaxis_title=x_title, yaxis_title=y_title)

        if config.BoxPlotOverTime.plot_fences:
            fig.update_traces(
                upperfence=stats["upper_fence"], lowerfence=stats["lower_fence"]
            )

        if self.overlay_data is not None:
            fig.add_trace(
                go.Scatter(
                    x=np.arange(self.overlay_data.shape[0]),
                    y=self.overlay_data,
                    mode=config.BoxPlotOverTime.scatter_mode,
                    showlegend=config.BoxPlotOverTime.showlegend,
                    name=config.BoxPlotOverTime.scatter_name,
                    marker_color=config.BoxPlotOverTime.scatter_color,
                )
            )
        self.fig = fig
        self.update_x_ticks(np.arange(self.data.shape[1]))
        return fig


class Histogram(BasePlotter):
    """
    Simple histogram plotter.
    """

    def __init__(self, data: np.ndarray, overlay_data=None):
        super().__init__(data, overlay_data)

    def create_plot(self, **kwargs) -> go.Figure:
        """Create a histogram plot.

        Returns:
            go.Figure: Plotly figure
        """
        x_title = kwargs.get("x_title", config.Histogram.x_title)
        y_title = kwargs.get("y_title", config.Histogram.y_title)
        fig = go.Figure(
            go.Histogram(y=self.data, opacity=0.9)
        ).update_layout(  # Flipping axes
            xaxis_title=x_title, yaxis_title=y_title
        )
        if self.overlay_data is not None:
            fig.add_hline(
                y=self.overlay_data,
                line_width=config.Histogram.line_width,
                line_color=config.Histogram.line_color,
                line_dash=config.Histogram.line_dash,
            )
        self.fig = fig
        return fig
