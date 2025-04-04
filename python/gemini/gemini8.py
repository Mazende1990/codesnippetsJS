# -*- coding: utf-8 -*-

import pytest

from requests import hooks


def _remove_first_char(value):
    """Removes the first character from a string."""
    return value[1:]


@pytest.mark.parametrize(
    'hooks_list, result',
    (
        (_remove_first_char, 'ata'),
        ([_remove_first_char, lambda x: None, _remove_first_char], 'ta'),
    ),
)
def test_hooks_dispatch(hooks_list, result):
    """Tests the dispatch_hook function with various hooks."""
    assert hooks.dispatch_hook('response', {'response': hooks_list}, 'Data') == result


def test_default_hooks():
    """Tests the default_hooks function to ensure it returns the expected default."""
    assert hooks.default_hooks() == {'response': []}