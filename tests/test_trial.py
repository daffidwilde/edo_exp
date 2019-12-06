""" Tests for the running trials. """

import os
from pathlib import Path

import pandas as pd
from edo.pdfs import Uniform
from hypothesis import given, settings
from hypothesis.strategies import floats, integers, tuples

from edo_exp import run_trial

INTS = integers(min_value=2, max_value=5)
SHAPES = tuples(INTS, INTS).map(sorted).filter(lambda x: x[0] <= x[1])
PROB = floats(min_value=0, max_value=1)
HALF_PROB = PROB.filter(lambda x: x > 0.5)

@settings(deadline=None, max_examples=30)
@given(
    size=INTS,
    row_limits=SHAPES,
    col_limits=SHAPES,
    max_iter=INTS,
    selection=HALF_PROB,
    mutation=PROB,
    seed=INTS,
)
def test_run_trial(size, row_limits, col_limits, max_iter, selection,
        mutation, seed):

    num_cores = None
    fitness = lambda x: pd.np.nan
    pdfs = [Uniform]
    data_path = Path("tmp")
    fitness_kwargs = {}

    run_trial(num_cores, fitness, size, row_limits, col_limits, pdfs, max_iter,
            selection, mutation, data_path, seed, fitness_kwargs)

    for gen in range(max_iter + 1):
        for ind in range(size):
            ind_path = data_path / str(gen) / str(ind)
            assert (ind_path / "main.csv").exists()
            assert (ind_path / "main.meta").exists()

    trial_fitness = pd.read_csv(data_path / "fitness.csv")
    assert all(trial_fitness.columns == ["fitness", "generation", "individual"])
    assert all(trial_fitness.dtypes == [float, int, int])
    assert list(trial_fitness["generation"].unique()) == list(range(max_iter + 1))
    assert list(trial_fitness["individual"].unique()) == list(range(size))
    assert len(trial_fitness) % size == 0

    os.system(f"rm -r {data_path}")
