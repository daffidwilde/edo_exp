""" Functions to define and run a trial. """

from sklearn.cluster import KMeans
from edo.pdfs import Uniform
import edo


def kmeans_fitness(dataframe, seed):
    """ Cluster the dataframe using the k-means algorithm into two parts.
    Evaluate the fitness to be the inertia at termination. """

    model = KMeans(n_clusters=2, random_state=seed)
    model.fit(dataframe)

    return model.inertia_


def run_trial(num_cores, root, size, row_limits, col_limits, mutation, seed):
    """ Run EDO with the given parameters, write the resultant data to file and
    return the histories. """

    data = root / "data"

    pop_history, fit_history = edo.run_algorithm(
        fitness=kmeans_fitness,
        size=size,
        row_limits=row_limits,
        col_limits=col_limits,
        families=[Uniform],
        max_iter=1000,
        mutation_prob=mutation,
        processes=num_cores,
        root=data,
        seed=seed,
        fitness_kwargs={"seed": seed},
    )

    return pop_history, fit_history
