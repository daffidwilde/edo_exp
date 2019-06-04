""" Function to define and run a trial. """

import edo
from edo.pdfs import Uniform


def run_trial(
    data_path,
    fitness,
    num_cores,
    size,
    row_limits,
    col_limits,
    selection,
    mutation,
    seed,
    fitness_kwargs,
):
    """ Run EDO with the given parameters, write the resultant data to file and
    return the histories. """

    Uniform.param_limits["bounds"] = [0, 1]

    edo.run_algorithm(
        fitness=fitness,
        size=size,
        row_limits=row_limits,
        col_limits=col_limits,
        families=[Uniform],
        max_iter=1000,
        best_prop=selection,
        mutation_prob=mutation,
        processes=num_cores,
        root=data_path,
        seed=seed,
        fitness_kwargs=fitness_kwargs,
    )

    return None
