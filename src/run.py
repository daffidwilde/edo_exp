""" Function to write a bash script for a set of experiments. """

import itertools
import os
import sys
from pathlib import Path


def get_idx(path):
    """ Get the last used index. """

    with open(path, "r") as idx_file:
        idx = int(idx_file.read())

    return idx


def make_dirs(root):
    """ Make job and data directories. """

    job_dir = Path(f"{root}/.job")
    data_dir = Path(f"/scratch/c.c1420099/edo_kmeans")

    job_dir.mkdir(exist_ok=True)
    data_dir.mkdir(exist_ok=True, parents=True)

    return job_dir


def get_job_files(job_dir, case, size, mut, seed):
    """ Get the name of, and files needed to run, the job. """

    mut_str = str(mut).split(".")[-1]
    name = f"edo_{case}_{size}_{mut_str}_{seed}"
    job = job_dir / f"{name}.job"
    out = job_dir / f"{name}.out"
    err = job_dir / f"{name}.err"

    return name, job, out, err


def main(num_cores, sizes, mutations, repetitions, idx=None):
    """ Write and submit bash scripts with the parameters for a series of runs.
    """

    if idx is None:
        idx = get_idx("idx.txt")

    job_dir = make_dirs(os.getcwd())
    args = itertools.product(
        [num_cores],
        ["bounded", "unbounded"],
        sizes,
        mutations,
        range(repetitions),
    )

    for idx, (cores, case, size, mut, seed) in enumerate(itertools.islice(
        args, idx, None
    )):

        job_name, job_file, out_file, err_file = get_job_files(
            job_dir, case, size, mut, seed
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
            job.write("source activate edo-kmeans\n\n")

            job.write("cd $HOME/src/edo_kmeans/src\n")
            job.write(f"python main.py {cores} {case} {size} {mut} {size}\n\n")

            job.write("conda deactivate\n")

        code = os.system(f"sbatch {job_file}")
        if code == 0:
            os.system(f"echo {idx} > idx.txt")
            continue
        else:
            print(f"Job limit reached. Last index {idx}")
            break


if __name__ == "__main__":

    NUM_CORES = int(sys.argv[1])
    SIZES = list(sys.argv[2].split(","))
    MUTATIONS = list(sys.argv[3].split(","))
    REPETITIONS = int(sys.argv[4])

    IDX = None
    if len(sys.argv) == 6:
        IDX = int(sys.argv[5])

    main(NUM_CORES, SIZES, MUTATIONS, REPETITIONS, IDX)
