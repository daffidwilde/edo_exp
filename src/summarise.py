""" Functions for summarising a trial. """

import os

import pandas as pd


def get_extremes(root, fit, max_gen):
    """ Get the best, median and worst performing individuals in the final
    population. Write them to file. """

    best_idx = fit.nsmallest(1, "fitness")["individual"].compute().iloc[0]
    worst_idx = fit.nlargest(1, "fitness")["individual"].compute().iloc[0]

    fit["diff"] = fit["fitness"] - fit["fitness"].quantile()
    median_idx = fit.nsmallest(1, "diff")["individual"].compute().iloc[0]

    for idx, case in zip(
        [best_idx, median_idx, worst_idx], ["best", "median", "worst"]
    ):

        path = root / "summary" / case
        os.system(f"cp -r {root}/{max_gen}/{idx} {path}")


def get_trial_info(summary, pop_history):
    """ Traverse the trial history and summarise some basic information about
    the individual datasets that have been generated. """

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
    info.to_csv(summary / "info.csv", index=False)


def summarise_trial(root, pop_history, fit_history):
    """ Summarise a run of an experiment by investigating the shape/size of the
    individuals created, and finding some descriptive individuals in the final
    population. """

    summary = root / "summary"
    summary.mkdir(exist_ok=True)

    max_gen = len(pop_history)
    fit = fit_history[fit_history["generation"] == max_gen]

    get_extremes(root, fit, max_gen)
    get_trial_info(summary, pop_history)
