""" Main function for a whole run of the experiment. """

import itertools
import sys

import dask
from dask.distributed import Client
from dask_jobqueue import SLURMCluster

from trials import run_trial


def main(num_cores, repetitions, case, size, max_iter):
    """ Attach to the client, then build and compute the tasks. """

    if case == "graphed":
        row_limits = [[100, 1000]]
        col_limits = [2, 2]
    elif case == "unbounded":
        row_limits = [1000, 100000]
        col_limits = [5, 100]

    tasks = (
        run_trial(*args)
        for args in itertools.product(
            [case],
            [size],
            [row_limits],
            [col_limits],
            [max_iter],
            range(repetitions),
        )
    )

    dask.compute(*tasks)


if __name__ == "__main__":

    NUM_CORES = int(sys.argv[1])
    REPETITIONS = int(sys.argv[2])
    CASE = str(sys.argv[3])
    SIZE = int(sys.argv[4])
    MAX_ITER = int(sys.argv[5])

    cluster = SLURMCluster(
        name="edo_kmeans_" + CASE,
        queue="compute",
        project="scw1337",
        processes=NUM_CORES,
        local_dirctory="/scratch/c.c1420099/tmp/",
    )

    cluster.adapt(minimum_cores=8)
    client = Client(cluster)
    main(NUM_CORES, REPETITIONS, CASE, SIZE, MAX_ITER)
