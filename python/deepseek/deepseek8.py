# -*- coding: utf-8 -*-
"""
Tests for request hooks functionality.

This module contains tests for the hook dispatch system in the requests library,
verifying both single hooks and multiple hook chaining behavior.
"""

import pytest
from requests import hooks


def remove_first_char(value):
    """Test hook that removes the first character from a string."""
    return value[1:]


def null_hook(value):
    """Test hook that does nothing (returns None)."""
    return None


@pytest.mark.parametrize(
    "hooks_list, expected_result",
    [
        # Single hook case
        (remove_first_char, "ata"),
        # Multiple hooks case
        ([remove_first_char, null_hook, remove_first_char], "ta"),
        # Edge case: empty hooks list should return original data
        ([], "Data"),
    ],
    ids=[
        "single_hook",
        "multiple_hooks",
        "empty_hooks_list",
    ]
)
def test_dispatch_hook(hooks_list, expected_result):
    """
    Test that hooks are properly dispatched and applied to response data.
    
    Args:
        hooks_list: Either a single hook or list of hooks to apply
        expected_result: The expected string after applying all hooks
    """
    # Setup
    hook_key = "response"
    hook_dict = {hook_key: hooks_list}
    test_data = "Data"
    
    # Execution
    result = hooks.dispatch_hook(hook_key, hook_dict, test_data)
    
    # Verification
    assert result == expected_result


def test_default_hooks():
    """Test that default hooks are properly initialized."""
    # Expected structure
    expected = {"response": []}
    
    # Verify
    assert hooks.default_hooks() == expected


@pytest.mark.parametrize(
    "hook_key, expected_default",
    [
        ("response", []),
        ("nonexistent", None),
    ]
)
def test_default_hooks_structure(hook_key, expected_default):
    """
    Test the structure and default values of the hooks dictionary.
    
    Args:
        hook_key: The hook key to test
        expected_default: Expected default value for this key
    """
    hooks_dict = hooks.default_hooks()
    assert hooks_dict.get(hook_key) == expected_default