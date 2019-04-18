""" Function to write a bash script for a set of experiments. """

import itertools
import os
import sys
from pathlib import Path


def main(num_cores, sizes, mutations, repetitions):
    """ Write a bash script with the parameters for a series of runs. """

    job_dir = Path(f"{os.getcwd()}/.job")
    data_dir = Path("/scratch/c.c1420099/edo_kmeans")

    job_dir.mkdir(exist_ok=True)
    data_dir.mkdir(parents=True, exist_ok=True)

    cases = ["bounded", "unbounded"]
    for cores, case, size, mut, seed in itertools.product(
        [num_cores], cases, sizes, mutations, range(repetitions)
    ):

        mut_str = str(mut).split(".")[-1]
        job_file = job_dir / f"edo_{case}_{size}_{mut_str}_{seed}.job"

        with open(job_file, "w") as job:
            job.write("#!/bin/bash --login\n\n")

            job.write("#SBATCH -A scw1337\n")
            job.write("#SBATCH -p compute\n")
            job.write("#SBATCH -t 24:00:00\n")
            job.write("#SBATCH --exclusive\n")
            job.write(f"#SBATCH --job-name={job_file}\n")
            job.write(f"#SBATCH --n-tasks={cores}\n")
            job.write(f"#SBATCH --ntasks-per-node={cores}\n\n")

            job.write("module load anaconda\n")
            job.write("source activate edo-kmeans\n\n")

            job.write("cd $SLURM_SUBMIT_DIR\n")
            job.write(f"python main.py {cores} {case} {size} {mut} {size}\n\n")

            job.write("conda deactivate")

        os.system(f"sbatch {job_file}")


if __name__ == "__main__":

    NUM_CORES = sys.argv[1]
    SIZES = list(sys.argv[2].split(","))
    MUTATIONS = list(sys.argv[3].split(","))
    REPETITIONS = int(sys.argv[4])

    main(NUM_CORES, SIZES, MUTATIONS, REPETITIONS)
