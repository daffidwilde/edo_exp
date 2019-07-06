""" Functions for summarising a trial. """

import os
import sys
import tarfile
from pathlib import Path

import numpy as np
import pandas as pd
from edo.run import _get_pop_history


def get_extremes(trial, fitness):
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

        ind, gen = fitness[["individual", "generation"]].iloc[idx, :]
        path = trial / "summary" / case
        path.mkdir(exist_ok=True)
        os.system(f"cp -r {trial}/data/{gen}/{ind}/* {path}")


def get_trial_info(data, summary, max_gen, fitness):
    """ Traverse the trial history and summarise some basic information about
    the individual datasets that have been generated. """

    info_dfs = []
    for gen, generation in enumerate(_get_pop_history(data, max_gen + 1)):
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
    info["fitness"] = fitness["fitness"]
    info.to_csv(summary / "main.csv", index=False)


def make_tarball(data):
    """ Compress the data in `root` to a tarball and remove the original. """

    with tarfile.open(str(data) + ".tar.gz", "w:gz") as tar:
        tar.add(data, arcname=os.path.basename(data))

    os.system(f"rm -rf {str(data)}")


def summarise_trial(trial, fitness, max_gen, size):
    """ Summarise a run of an experiment by investigating the shape/size of the
    individuals created, and finding some descriptive individuals in the final
    population. """

    if len(fitness) == (max_gen + 1) * size:
        data = trial / "data"
        summary = trial / "summary"
        summary.mkdir(exist_ok=True)

        get_extremes(trial, fitness)
        get_trial_info(data, summary, max_gen, fitness)
        make_tarball(data)
        print(trial, "summarised.")

    else:
        print(trial, "incomplete. Moving on.")


def main(name, max_gen, root=None):
    """ Crawl through the `root` directory of an experiment and if a trial has
    been completed, summarise the data and make a tarball of it. Otherwise, move
    on. """

    root = Path(root) if root is not None else Path(f"experiments/{name}")

    try:
        experiments = (
            path
            for path in root.iterdir()
            if path.is_dir() and path.name.startswith("size")
        )

        for experiment in experiments:
            size = int(experiment.name.split("_")[1])
            trials = (path for path in experiment.iterdir() if path.is_dir())

            for trial in trials:

                try:
                    data = trial / "data"
                    fitness = pd.read_csv(data / "fitness.csv")
                    summarise_trial(trial, fitness, max_gen, size)
                except FileNotFoundError:
                    print(trial, "already summarised.")

    except FileNotFoundError:
        print("Not begun yet.")


if __name__ == "__main__":
    NAME = str(sys.argv[1])
    MAX_GEN = int(sys.argv[2])
    ROOT = None
    if len(sys.argv) == 4:
        ROOT = str(sys.argv[3])

    main(NAME, MAX_GEN, ROOT)
