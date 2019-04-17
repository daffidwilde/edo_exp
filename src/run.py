""" Function to write a bash script for a set of experiments. """

import itertools
import os
import sys


def get_arguments(args, idx):
    """ Get the set of arguments at index `idx`. """

    iter_args = iter(itertools.islice(args, idx, None))
    return next(iter_args, "STOP")


def main(idx, num_cores, sizes, mutations, repetitions):
    """ Write a bash script with the parameters for a series of runs. """

    cases = ["bounded", "unbounded"]
    args = itertools.product(
        [num_cores], cases, sizes, mutations, range(repetitions)
    )

    arguments = get_arguments(args, idx)

    if arguments == "STOP":
        return

    cores, case, size, mutation, seed = arguments
    with open("run.sh", "w") as bash:

        jobscript = (
            "#!/bin/bash --login\n\n"
            + f"#SBATCH -J edo_kmeans_{case}\n"
            + f"#SBATCH --ntasks={cores}\n"
            + f"#SBATCH --ntasks-per-node={cores}\n"
            + "#SBATCH -A scw1337\n"
            + "#SBATCH -p compute\n"
            + "#SBATCH -t 23:59:59\n"
            + "#SBATCH --exclusive\n\n"
        )
        bash.write(jobscript)

        bash.write("export THIS_SCRATCH=/scratch/$USER/$SLURM_JOBID\n")
        bash.write("rm -rf $THIS_SCRATCH\n")
        bash.write("mkdir -p $THIS_SCRATCH\n")
        bash.write("cd $THIS_SCRATCH\n")
        bash.write("cp -r $SLURM_SUBMIT_DIR/.. .\n\n")

        bash.write("module load anaconda\n")
        bash.write("conda env create -f ../environment.yml\n")
        bash.write("source activate edo-kmeans\n\n")

        bash.write("cd src\n")
        bash.write(f"python main.py {cores} {case} {size} {mutation} {seed}\n")

        bash.write("conda deactivate\n")
        bash.write("conda env remove -n edo-kmeans")

    os.system("chmod +x run.sh")
    os.system("./run.sh")

    main(idx + 1, num_cores, sizes, mutations, repetitions)


if __name__ == "__main__":

    IDX = int(sys.argv[1])
    NUM_CORES = sys.argv[2]
    SIZES = list(sys.argv[3].split(","))
    MUTATIONS = list(sys.argv[4].split(","))
    REPETITIONS = int(sys.argv[5])

    main(IDX, NUM_CORES, SIZES, MUTATIONS, REPETITIONS)
