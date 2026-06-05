from unittest.mock import patch

from coding_agent.file_generator import generate_file


MOCK_RESPONSE = "mocked response"


def test_output_has_path_key():
    with patch("coding_agent.file_generator.get_llm_response", return_value=MOCK_RESPONSE):
        result = generate_file(_node_route_blueprint(), _node_react_jwt_rules())
    assert "path" in result


def test_output_has_content_key():
    with patch("coding_agent.file_generator.get_llm_response", return_value=MOCK_RESPONSE):
        result = generate_file(_node_route_blueprint(), _node_react_jwt_rules())
    assert "content" in result


def test_path_preserved():
    with patch("coding_agent.file_generator.get_llm_response", return_value=MOCK_RESPONSE):
        result = generate_file(_node_route_blueprint(), _node_react_jwt_rules())
    assert result["path"] == "src/routes/workspaces.js"


def test_content_returned():
    with patch("coding_agent.file_generator.get_llm_response", return_value=MOCK_RESPONSE):
        result = generate_file(_node_route_blueprint(), _node_react_jwt_rules())
    assert result["content"] == MOCK_RESPONSE


def test_content_not_empty():
    with patch("coding_agent.file_generator.get_llm_response", return_value=MOCK_RESPONSE):
        result = generate_file(_node_route_blueprint(), _node_react_jwt_rules())
    assert len(result["content"]) > 0


def test_different_path_preserved():
    blueprint = {"path": "src/pages/Home.jsx", "type": "page", "purpose": "Home page"}
    with patch("coding_agent.file_generator.get_llm_response", return_value=MOCK_RESPONSE):
        result = generate_file(blueprint, _node_react_jwt_rules())
    assert result["path"] == "src/pages/Home.jsx"


def test_config_file_path_preserved():
    blueprint = {
        "path": "package.json",
        "type": "config",
        "purpose": "Node.js dependencies and scripts",
    }
    with patch("coding_agent.file_generator.get_llm_response", return_value=MOCK_RESPONSE):
        result = generate_file(blueprint, _node_react_jwt_rules())
    assert result["path"] == "package.json"


def test_missing_path_falls_back():
    with patch("coding_agent.file_generator.get_llm_response", return_value=MOCK_RESPONSE):
        result = generate_file({}, _node_react_jwt_rules())
    assert result["path"] == "unknown"


def test_llm_called_with_coder_model():
    with patch("coding_agent.file_generator.get_llm_response", return_value=MOCK_RESPONSE) as mock:
        generate_file(_node_route_blueprint(), _node_react_jwt_rules())
    mock.assert_called_once()
    _assert_called_with_kwarg(mock, "model", "qwen/qwen3-next-80b-a3b-instruct")


def test_llm_called_with_prompt():
    with patch("coding_agent.file_generator.get_llm_response", return_value=MOCK_RESPONSE) as mock:
        generate_file(_node_route_blueprint(), _node_react_jwt_rules())
    mock.assert_called_once()
    prompt_arg = _get_arg(mock, 0)
    assert "src/routes/workspaces.js" in prompt_arg
    assert "Express.js" in prompt_arg
    assert "React" in prompt_arg
    assert "PostgreSQL" in prompt_arg
    assert "JWT" in prompt_arg


def test_llm_called_once():
    with patch("coding_agent.file_generator.get_llm_response", return_value=MOCK_RESPONSE) as mock:
        generate_file(_node_route_blueprint(), _node_react_jwt_rules())
    mock.assert_called_once()


def test_empty_llm_response_allowed():
    with patch("coding_agent.file_generator.get_llm_response", return_value=""):
        result = generate_file(_node_route_blueprint(), _node_react_jwt_rules())
    assert isinstance(result["content"], str)
    assert result["content"] == ""


def test_multiple_calls_independent():
    blueprint_a = {"path": "src/app.js", "type": "source", "purpose": "App entry"}
    blueprint_b = {"path": "src/server.js", "type": "source", "purpose": "Server entry"}
    with patch("coding_agent.file_generator.get_llm_response", return_value=MOCK_RESPONSE):
        result_a = generate_file(blueprint_a, _node_react_jwt_rules())
        result_b = generate_file(blueprint_b, _node_react_jwt_rules())
    assert result_a["path"] == "src/app.js"
    assert result_b["path"] == "src/server.js"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _get_arg(mock, index):
    return mock.call_args[0][index]


def _assert_called_with_kwarg(mock, key, value):
    _, kwargs = mock.call_args
    assert kwargs.get(key) == value, (
        f"Expected {key}={value!r}, got {kwargs.get(key)!r}"
    )


# ---------------------------------------------------------------------------
# Sample data
# ---------------------------------------------------------------------------


def _node_route_blueprint():
    return {
        "path": "src/routes/workspaces.js",
        "type": "module",
        "purpose": "workspaces API routes",
    }


def _node_react_jwt_rules():
    return {
        "backend_framework": "Express.js",
        "frontend_framework": "React",
        "database": "PostgreSQL",
        "auth_method": "JWT",
        "deployment": "AWS",
        "required_pages": ["Home", "Login", "Dashboard", "Settings"],
        "required_backend_modules": ["workspaces", "projects", "tasks"],
    }
