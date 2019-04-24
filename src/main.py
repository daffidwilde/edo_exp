""" Main function for a run of an experiment. """

import sys
from pathlib import Path

from trial import run_trial

ROOT = "/scratch/c.c1420099/edo_kmeans"


def main(num_cores, case, size, mutation, seed):
    """ Run a trial, summarise it, then compress the trial to a tarball and
    delete the original data. """

    root = Path(ROOT) / case / f"size_{size}_mu_{mutation}" / str(seed)
    root.mkdir(exist_ok=True, parents=True)

    if case == "bounded":
        row_limits = [100, 1000]
        col_limits = [2, 2]
    elif case == "unbounded":
        row_limits = [1000, 100000]
        col_limits = [5, 100]

    run_trial(num_cores, root, size, row_limits, col_limits, mutation, seed)

if __name__ == "__main__":

    NUM_CORES = int(sys.argv[1])
    CASE = str(sys.argv[2])
    SIZE = int(sys.argv[3])
    MUTATION = float(sys.argv[4])
    SEED = int(sys.argv[5])

    main(NUM_CORES, CASE, SIZE, MUTATION, SEED)
