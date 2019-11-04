""" Function to define and run a trial. """

import edo

def run_trial(
    num_cores,
    fitness,
    size,
    row_limits,
    col_limits,
    pdfs,
    max_iter,
    selection,
    mutation,
    data_path,
    seed,
    fitness_kwargs,
):
    """ Run EDO with the given parameters. Write the resultant data to file. """

    edo.run_algorithm(
        fitness=fitness,
        size=size,
        row_limits=row_limits,
        col_limits=col_limits,
        families=pdfs,
        max_iter=max_iter,
        best_prop=selection,
        mutation_prob=mutation,
        processes=num_cores,
        root=data_path,
        seed=seed,
        fitness_kwargs=fitness_kwargs,
    )

    return None
