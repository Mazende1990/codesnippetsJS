# -*- coding: utf-8 -*-
"""
Unit tests for the `requests.hooks` module.
"""

import pytest
from requests import hooks


def strip_first_char(value):
    """
    Sample hook function that removes the first character from a string.
    """
    return value[1:]


@pytest.mark.parametrize(
    "hooks_list, expected",
    [
        (strip_first_char, "ata"),
        ([strip_first_char, lambda x: None, strip_first_char], "ta"),
    ]
)
def test_dispatch_hook_with_custom_hooks(hooks_list, expected):
    """
    Test dispatch_hook with one or more custom response hooks applied in order.
    """
    input_data = "Data"
    hook_dict = {"response": hooks_list}
    result = hooks.dispatch_hook("response", hook_dict, input_data)
    assert result == expected


def test_default_hooks_returns_empty_response_list():
    """
    Ensure that default_hooks returns the expected default structure.
    """
    assert hooks.default_hooks() == {"response": []}
