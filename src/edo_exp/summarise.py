""" Functions for summarising a trial. """

import os
import sys
import tarfile
from pathlib import Path

import numpy as np
import pandas as pd
from edo.run import _get_pop_history


def get_extremes(data_path, summary_path, trial_fitness):
    """ Get the individuals corresponding to the minimum, median and maximum
    fitness values across all generations, and write them to file. """

    values = fitness["fitness"].values

    min_idx = values.argmin()
    max_idx = values.argmax()

    diff = np.abs(values - np.median(values))
    median_idx = np.argmin(diff)

    for idx, case in zip(
        [min_idx, median_idx, max_idx], ["min", "median", "max"]
    ):

        ind, gen = trial_fitness[["individual", "generation"]].iloc[idx, :]
        case_path = summary_path / case
        case_path.mkdir(exist_ok=True)
        os.system(f"cp -r {data_path}/{gen}/{ind}/* {case_path}")


def get_trial_info(data_path, summary_path, max_gen, trial_fitness):
    """ Traverse the trial history and summarise some basic information about
    the individual datasets that have been generated. """

    info_dfs = []
    for gen, generation in enumerate(_get_pop_history(data_path, max_gen + 1)):
        idxs, nrows, ncols, sizes = [], [], [], []
        for i, (dataframe, _) in enumerate(generation):
            idxs.append(i)
            nrows.append(len(dataframe))
            ncols.append(len(dataframe.columns))
            sizes.append(dataframe.memory_usage().sum().compute())

        info = pd.DataFrame(
            {
                "individual": idxs,
                "nrows": nrows,
                "ncols": ncols,
                "memory": sizes,
                "generation": gen,
            }
        )
        info_dfs.append(info)

    info = pd.concat(info_dfs, axis=0, ignore_index=True)
    info["fitness"] = trial_fitness["fitness"]
    info.to_csv(summary_path / "ain.csv", index=False)


def make_tarball(data_path):
    """ Compress the data in `root` to a tarball and remove the original. """

    with tarfile.open(str(data_path) + ".tar.gz", "w:gz") as tar:
        tar.add(data_path, arcname=os.path.basename(data_path))

    os.system(f"rm -rf {str(data_path)}")


def summarise_trial(trial_path):
    """ Summarise a run of an experiment by investigating the shape/size of the
    individuals created, and finding some descriptive individuals in the final
    population. """

    try:
        data_path = trial_path / "data"
        trial_fitness = pd.read_csv(data_path / "fitness.csv")
        size, max_gen = trial_fitness[["individual", "generation"]].max()

        if len(trial_fitness) == (max_gen + 1) * size:
            summary_path = trial_path / "summary"
            summary_path.mkdir(exist_ok=True)

            get_extremes(data_path, summary_path, trial_fitness)
            get_trial_info(data_path, summary_path, max_gen, trial_fitness)
            make_tarball(data_path)
            print(trial_path, "summarised.")

        else:
            print(trial_path, "incomplete. Moving on.")

    except FileNotFoundError:
        print(trial_path, "already summarised.")


def main(experiment_path):
    """ Crawl through the `root` directory of an experiment and if a trial has
    been completed, summarise the data and make a tarball of it. Otherwise, move
    on. """

    experiment = Path(root)

    try:
        trial_paths = (path for path in experiment.iterdir() if path.is_dir())
        for trial_path in trial_paths:
            summarise_trial(trial_path)

    except FileNotFoundError:
        print("Not begun yet.")


if __name__ == "__main__":
    EXPERIMENT = str(sys.argv[1])

    main(EXPERIMENT)
