# import os  # Replace this with pathlib
from datetime import datetime
from os import PathLike
from pathlib import Path


def generate_path(project: str, exp_name: str, basepath: str) -> PathLike:
    """Create sub-directories for saving experimental data.

    Args:
        basepath (regexp, optional): IO str for the path of experiment
        folder. Defaults to r'Downloads'.
        exp_name (str, optional): experiment name. Defaults to
        'new_experiment'.
        new (bool, optional): whether the experiment is old or new.
        Defaults to True.

        if False: you want to save the data in a old experiment folder,
        or a experiment folder that do not have date and time.
        if you want to save in a old folder
        give the exp_name same as the full folder name with date and time
        as previous one.

        if True: give the experiment name only, no need to give date
        and time.

    """
    current_time = datetime.now()
    hour_min_sec = current_time.strftime("_%H-%M-%S")  # _%d-%m-%y
    year_month = current_time.strftime("%Y-%m")
    date = current_time.strftime("%d")
    exp_name = exp_name + hour_min_sec
    project = project
    path = Path.cwd() / basepath / project / year_month / date / exp_name
    if path.exists():
        path = path.parent / (path.stem + current_time.strftime("-%f"))
    path.mkdir(parents=True, exist_ok=True)

    return path
