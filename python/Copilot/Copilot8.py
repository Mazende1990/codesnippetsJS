# -*- coding: utf-8 -*-

import pytest
from requests import hooks

def hook(value):
    """
    A simple hook function that returns the input value excluding the first character.
    """
    return value[1:]

@pytest.mark.parametrize(
    'hooks_list, result', [
        (hook, 'ata'),
        ([hook, lambda x: None, hook], 'ta'),
    ]
)
def test_hooks(hooks_list, result):
    """
    Test the dispatch_hook function with various hook lists and expected results.
    """
    assert hooks.dispatch_hook('response', {'response': hooks_list}, 'Data') == result

def test_default_hooks():
    """
    Test the default_hooks function to ensure it returns the expected default hooks.
    """
    assert hooks.default_hooks() == {'response': []}