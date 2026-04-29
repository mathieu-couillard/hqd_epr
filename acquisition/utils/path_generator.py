# import os  # Replace this with pathlib
from datetime import datetime
from os import PathLike
from pathlib import Path


def generate_path(project: str, exp_name: str, basepath: str) -> tuple[PathLike, PathLike, PathLike]:
    """Create sub-directories for saving experimental data.

    Args:
        basepath (regexp): IO str for the path of experiment
        folder.
        exp_name (str): experiment name.

    Returns:
        path (Path): Path to the created directories
    """
    current_time = datetime.now()
    hour_min_sec = current_time.strftime("_%H-%M-%S")  # _%d-%m-%y
    year_month = current_time.strftime("%Y-%m")
    date = current_time.strftime("%d")
    exp_name = exp_name + hour_min_sec
    path = Path.cwd() / basepath / project / year_month / date / exp_name
    if path.exists():
        path = path.parent / (path.stem + current_time.strftime("-%f"))
    path.mkdir(parents=True, exist_ok=True)
    data_path = path / "data"
    data_path.mkdir(parents=True, exist_ok=True)
    fig_path = path / "fig"
    fig_path.mkdir(parents=True, exist_ok=True)

    return path, data_path, fig_path
