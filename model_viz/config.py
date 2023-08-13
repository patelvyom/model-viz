import configparser
import os
from datetime import datetime

# APP Settings
MODEL_VIZ_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
runtime_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
config_file = os.path.join(MODEL_VIZ_BASE_DIR, "config.ini")

configuration = configparser.ConfigParser()
configuration.read(config_file)
output_dir = configuration.get("APP", "output_dir")
output_filename: str = os.path.join(
    output_dir, f'{runtime_str}_{configuration.get("APP", "output_filename")}.pdf'
)


# Plotter Settings
class Plotter:
    output_dir: str = os.path.join(output_dir, runtime_str)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    output_file_format: str = configuration.get("PLOTTER", "output_format")
    export_engine: str = configuration.get("PLOTTER", "export_engine")
    width: int = configuration.getint("PLOTTER", "width")
    height: int = configuration.getint("PLOTTER", "height")
    is_xlabel_date: bool = configuration.getboolean("PLOTTER", "is_xlabel_date")
    day_zero: str = configuration.get("PLOTTER", "day_zero")
    graph_div_style: dict = {
        "height": configuration.get("PLOTTER", "graph_div_height"),
        "width": "100%",
    }
    theme: str = configuration.get("PLOTTER", "theme")
    desired_tick_labels: int = configuration.getint("PLOTTER", "desired_tick_labels")


class Histogram2D(Plotter):
    title: str = configuration.get("HISTOGRAM2D", "title")
    x_title: str = configuration.get("HISTOGRAM2D", "x_title")
    y_title: str = configuration.get("HISTOGRAM2D", "y_title")
    colorbar_title: str = configuration.get("HISTOGRAM2D", "colorbar_title")
    colorbar_titleside: str = configuration.get("HISTOGRAM2D", "colorbar_titleside")
    histfunc: str = configuration.get("HISTOGRAM2D", "histfunc")
    scatter_mode: str = configuration.get("HISTOGRAM2D", "scatter_mode")
    scatter_color: str = configuration.get("HISTOGRAM2D", "scatter_color")
    colorscale: str = configuration.get("HISTOGRAM2D", "colorscale")
    scatter_name: str = configuration.get("HISTOGRAM2D", "scatter_name")


class BoxPlotOverTime(Plotter):
    title: str = configuration.get("BOXPLOTOVERTIME", "title")
    x_title: str = configuration.get("BOXPLOTOVERTIME", "x_title")
    y_title: str = configuration.get("BOXPLOTOVERTIME", "y_title")
    boxpoints: bool = configuration.getboolean("BOXPLOTOVERTIME", "boxpoints")
    showlegend: bool = configuration.getboolean("BOXPLOTOVERTIME", "showlegend")
    scatter_mode: str = configuration.get("BOXPLOTOVERTIME", "scatter_mode")
    scatter_color: str = configuration.get("BOXPLOTOVERTIME", "scatter_color")
    plot_fences: bool = configuration.getboolean("BOXPLOTOVERTIME", "plot_fences")
    scatter_name: str = configuration.get("BOXPLOTOVERTIME", "scatter_name")


class Histogram(Plotter):
    x_title: str = configuration.get("HISTOGRAM", "x_title")
    y_title: str = configuration.get("HISTOGRAM", "y_title")
