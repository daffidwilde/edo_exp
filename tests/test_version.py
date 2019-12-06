""" Test the version number. """

import re
import edo_exp


def test_version():
    """ Assert that the version for `edo_exp` is a string containing only
    numbers, full-stops and letters. """

    version = edo_exp.__version__
    pattern = r'[^\.a-z0-9]'

    assert isinstance(version, str)
    assert re.search(version, pattern) is None
