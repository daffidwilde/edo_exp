""" Main function for a run of an experiment. """

import sys
from pathlib import Path

from summarise import summarise_trial
from tar import make_tarball
from trial import run_trial

ROOT = "/scratch/c.c1420099/edo_kmeans"


def main(num_cores, case, size, mutation, seed):
    """ Run a trial, summarise it, then compress the trial to a tarball and
    delete the original data. """

    root = Path(ROOT) / case / f"size_{size}_mu_{mutation}" / str(seed)

    if case == "bounded":
        row_limits = [100, 1000]
        col_limits = [2, 2]
    elif case == "unbounded":
        row_limits = [1000, 100000]
        col_limits = [5, 100]

    pop_history, fit_history = run_trial(
        num_cores, root, size, row_limits, col_limits, mutation, seed
    )

    summarise_trial(root, pop_history, fit_history)
    make_tarball(root)


if __name__ == "__main__":

    NUM_CORES = int(sys.argv[1])
    CASE = str(sys.argv[2])
    SIZE = int(sys.argv[3])
    MUTATION = float(sys.argv[4])
    SEED = int(sys.argv[5])

    main(NUM_CORES, CASE, SIZE, MUTATION, SEED)
