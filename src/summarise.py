""" Functions for summarising a trial. """

import os
import sys
import tarfile
from pathlib import Path

import numpy as np
import pandas as pd
from edo.run import _get_pop_history


def get_extremes(trial, fitness, max_gen):
    """ Get the best, median and worst performing individuals in the final
    population. Write them to file. """

    fit = fitness[fitness["generation"] == max_gen]
    best_idx = np.argmin(fit["fitness"].values)
    worst_idx = np.argmax(fit["fitness"].values)

    median = np.median(fit["fitness"])
    diff = fit["fitness"] - median
    median_idx = np.argmin(diff.values)

    for idx, case in zip(
        [best_idx, median_idx, worst_idx], ["best", "median", "worst"]
    ):

        path = trial / "summary" / case
        os.system(f"cp -r {trial}/data/{max_gen}/{idx} {path}")


def get_trial_info(data, summary, max_gen):
    """ Traverse the trial history and summarise some basic information about
    the individual datasets that have been generated. """

    pop_history = _get_pop_history(data, max_gen + 1)

    info_dfs = []
    for gen, generation in enumerate(pop_history):
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

        fitness.to_csv(summary / "fitness.csv")
        get_extremes(trial, fitness, max_gen)
        get_trial_info(data, summary, max_gen)
        make_tarball(data)
        print(trial, "summarised.")

    else:
        print(trial, "incomplete. Moving on.")


def main(max_gen):
    """ Crawl through the `root` directory and if a trial has been completed,
    summarise the data and make a tarball of it. Otherwise, move on. """

    for case in ["bounded", "unbounded"]:
        root = Path("/scratch/c.c1420099/edo_kmeans") / case

        try:
            experiments = (
                path
                for path in root.iterdir()
                if path.is_dir()
                and path.name.startswith("size")
            )

            for experiment in experiments:
                size = int(experiment.name.split("_")[1])
                trials = (
                    path for path in experiment.iterdir() if path.is_dir()
                )
                for trial in trials:
                    try:
                        data = trial / "data"
                        fitness = pd.read_csv(data / "fitness.csv")
                        summarise_trial(trial, fitness, max_gen, size)
                    except FileNotFoundError:
                        print(trial, "already summarised.")
        except FileNotFoundError:
            print(case, "not begun yet.")


if __name__ == "__main__":
    MAX_GEN = int(sys.argv[1])
    main(MAX_GEN)
