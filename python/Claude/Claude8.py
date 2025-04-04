# -*- coding: utf-8 -*-
"""Tests for the requests.hooks module functionality."""

import pytest
from requests import hooks


def test_default_hooks():
    """Test that default_hooks returns the expected empty hooks dictionary."""
    assert hooks.default_hooks() == {'response': []}


def hook(value):
    """Simple hook function that returns all but the first character of value."""
    return value[1:]


@pytest.mark.parametrize(
    'hooks_list, expected_result',
    [
        # Single hook function
        (hook, 'ata'),
        
        # Multiple hooks: first removes first char, second is no-op, third removes first char again
        ([hook, lambda x: None, hook], 'ta'),
    ],
    ids=['single_hook', 'multiple_hooks']
)
def test_dispatch_hook(hooks_list, expected_result):
    """Test that dispatch_hook correctly processes the data through the hooks chain."""
    initial_data = 'Data'
    hooks_dict = {'response': hooks_list}
    
    result = hooks.dispatch_hook('response', hooks_dict, initial_data)
    
    assert result == expected_result