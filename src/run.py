""" Function to write a bash script for a set of experiments. """

import itertools
import os
import sys


def main(
    num_cores=8, sizes=[100, 500, 1000], mutations=[0.001, 0.01, 0.05], repetitions=50
):
    """ Write a bash script with the parameters for a series of runs. """

    cases = ["bounded", "unbounded"]
    with open("run.sh", "w") as bash:
        for cores, case, size, mutation, seed in itertools.product(
            [num_cores], cases, sizes, mutations, range(repetitions)
        ):
            bash.write(
                f"python main.py {cores} {case} {size} {mutation} {seed}\n"
            )

    os.system("chmod +x run.sh")


if __name__ == "__main__":

    NUM_CORES = sys.argv[1]
    SIZES = list(sys.argv[2].split(","))
    MUTATIONS = list(sys.argv[3].split(","))
    REPETITIONS = int(sys.argv[4])

    main(NUM_CORES, SIZES, MUTATIONS, REPETITIONS)
