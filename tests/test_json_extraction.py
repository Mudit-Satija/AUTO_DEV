#!/usr/bin/env python3
"""Test robust JSON extraction from LLM responses."""

import json
import pytest
from planning_agents.shared.json_utils import extract_json


def test_plain_json_object():
    text = '{"method": "JWT", "storage": "httpOnly cookies"}'
    result = extract_json(text)
    assert result["method"] == "JWT"


def test_plain_json_array():
    text = '[{"method": "GET", "path": "/api/auth/login"}]'
    result = extract_json(text)
    assert len(result) == 1
    assert result[0]["method"] == "GET"


def test_surrounding_text_before_and_after():
    text = "Here's the result:\n{\"framework\": \"FastAPI\"}\nHope this helps!"
    result = extract_json(text)
    assert result["framework"] == "FastAPI"


def test_fenced_json():
    text = '```json\n{"key": "value"}\n```'
    result = extract_json(text)
    assert result["key"] == "value"


def test_fenced_json_without_lang():
    text = '```\n{"key": "value"}\n```'
    result = extract_json(text)
    assert result["key"] == "value"


def test_fenced_json_with_surrounding_text():
    text = "Here is the JSON:\n```json\n{\"framework\": \"React\"}\n```\nEnd."
    result = extract_json(text)
    assert result["framework"] == "React"


def test_malformed_json_raises():
    with pytest.raises((ValueError, json.JSONDecodeError)):
        extract_json("This is not JSON at all")


def test_non_string_input_raises():
    with pytest.raises(ValueError, match="Expected string"):
        extract_json(123)


def test_empty_braces_not_found():
    with pytest.raises((ValueError, json.JSONDecodeError)):
        extract_json("Some text without braces here")
