""" Function to write a bash script for a set of experiments. """

import itertools
import os
import sys
from pathlib import Path


def get_idx(path):
    """ Get the last used index. """

    try:
        with open(path, "r") as idx_file:
            idx = int(idx_file.read())

    except FileNotFoundError:
        with open(path, "w") as idx_file:
            idx = 0
            idx_file.write(idx)

    return idx


def make_dirs(root, name):
    """ Make job and data directories. """

    job_dir = Path(f"{root}/.job")
    data_dir = Path(f"/scratch/c.c1420099/edo/{name}")

    job_dir.mkdir(exist_ok=True, parents=True)
    data_dir.mkdir(exist_ok=True, parents=True)

    return job_dir


def get_job_files(job_dir, name, size, sel, mut, seed):
    """ Get the name of, and files needed to run, the job. """

    sel_str = str(sel).split(".")[-1]
    mut_str = str(mut).split(".")[-1]
    job_name = f"edo_{name}_{size}_{sel_str}_{mut_str}_{seed}"
    job_file = job_dir / f"{job_name}.job"
    out_file = job_dir / f"{job_name}.out"
    err_file = job_dir / f"{job_name}.err"

    return job_name, job_file, out_file, err_file


def main(
    name, num_cores, sizes, selections, mutations, repetitions, index=None
):
    """ Write and submit bash scripts with the parameters for a series of runs,
    stopping when the job limit has been reached. """

    index_path = f"$HOME/experiments/{name}/idx.txt"
    if index is None:
        index = get_idx(index_path)

    job_dir = make_dirs(os.getcwd(), name)
    args = itertools.product(
        [num_cores], sizes, selections, mutations, range(repetitions)
    )

    for idx, (cores, size, sel, mut, seed) in enumerate(
        itertools.islice(args, index, None)
    ):
        job_name, job_file, out_file, err_file = get_job_files(
            job_dir, name, size, sel, mut, seed
        )

        with open(job_file, "w") as job:
            job.write("#!/bin/bash --login\n\n")

            job.write("#SBATCH -A scw1337\n")
            job.write("#SBATCH -p compute\n")
            job.write("#SBATCH -t 48:00:00\n")
            job.write("#SBATCH --exclusive\n")
            job.write(f"#SBATCH --job-name={job_name}\n")
            job.write(f"#SBATCH -o {out_file}\n")
            job.write(f"#SBATCH -e {err_file}\n")
            job.write(f"#SBATCH --ntasks={cores}\n")
            job.write(f"#SBATCH --ntasks-per-node={int(cores / 2)}\n\n")

            job.write("module load anaconda\n")
            job.write("source activate edo-exp\n\n")

            job.write(f"cd $HOME/experiments/{name}\n")
            job.write(
                f"python main.py {name} {cores} {size} {sel} {mut} {seed}\n\n"
            )

            job.write("conda deactivate\n")

        code = os.system(f"sbatch {job_file}")
        os.system(f"echo {idx} > {index_path}")
        if code != 0:
            print(f"Job limit reached. Last index {idx}")
            break


if __name__ == "__main__":

    NAME = str(sys.argv[1])
    NUM_CORES = int(sys.argv[2])
    SIZES = list(sys.argv[3].split(","))
    SELECTIONS = list(sys.argv[4].split(","))
    MUTATIONS = list(sys.argv[5].split(","))
    REPETITIONS = int(sys.argv[6])

    IDX = None
    if len(sys.argv) == 8:
        IDX = int(sys.argv[7])

    main(NAME, NUM_CORES, SIZES, SELECTIONS, MUTATIONS, REPETITIONS, IDX)
