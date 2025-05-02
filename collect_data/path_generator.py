# import os  # Replace this with pathlib
from pathlib import Path
from datetime import datetime

from experiment_config import EXPERIMENT_BASE_PATH


class experiment:
    """_summary_
    basepath : experiment location. Default: Downloads
    exp_name: experiment name. Default: new_experiment

    new: {True | False} whether the experiment is old or new. Default: True,

    if False: you want to save the data in a old experiment folder,
    or a experiment folder that do not have date and time.
    if you want to save in a old folder
    give the exp_name same as the full folder name with date and time
    as previous one.

    if True: give the experiment name only, no need to give date and time.
    """

    def __init__(self, project, exp_name, basepath=EXPERIMENT_BASE_PATH, new=True):
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
        self._basepath = basepath
        self._exp_name = exp_name
        if new:
            self._datetime = datetime.now()
            self._timestamp = self._datetime.strftime("_%H-%M-%S")  # _%d-%m-%y
            self._year_month = self._datetime.strftime("%Y-%m")
            self._date = self._datetime.strftime("%d")
            self._exp_name = self._exp_name + self._timestamp
            self.project = project
            self._path = (
                Path.cwd()
                / self._basepath
                / self.project
                / self._year_month
                / self._date
                / self._exp_name
            )
            self._path.mkdir()

    def get_path(self):
        """Get the path to
        returns the experiment folder path created or
        located during the initialization.
        Returns:
            str: experiment folder path
        """
        return self._path


if __name__ == "__main__":
    d = experiment("project", "experiment").get_path()
    print(d)
