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
output_file_name: str = os.path.join(
    configuration.get(
        "APP", "output_filename", fallback=f"model_viz_{runtime_str}.pdf"
    ),
    runtime_str,
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


class Histogram2D(Plotter):
    title: str = configuration.get("HISTOGRAM2D", "title")
    x_title: str = configuration.get("HISTOGRAM2D", "x_title")
    y_title: str = configuration.get("HISTOGRAM2D", "y_title")
    colorbar_title: str = configuration.get("HISTOGRAM2D", "colorbar_title")
    colorbar_titleside: str = configuration.get("HISTOGRAM2D", "colorbar_titleside")
    histfunc: str = configuration.get("HISTOGRAM2D", "histfunc")
    scatter_mode: str = configuration.get("HISTOGRAM2D", "scatter_mode")
    colorscale: str = configuration.get("HISTOGRAM2D", "colorscale")


class BoxPlotOverTime(Plotter):
    title: str = configuration.get("BOXPLOTOVERTIME", "title")
    x_title: str = configuration.get("BOXPLOTOVERTIME", "x_title")
    y_title: str = configuration.get("BOXPLOTOVERTIME", "y_title")
    boxpoints: bool = configuration.getboolean("BOXPLOTOVERTIME", "boxpoints")
    showlegend: bool = configuration.getboolean("BOXPLOTOVERTIME", "showlegend")
    scatter_mode: str = configuration.get("BOXPLOTOVERTIME", "scatter_mode")


# HDFReader Settings
