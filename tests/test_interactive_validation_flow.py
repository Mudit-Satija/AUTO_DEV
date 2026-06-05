from schemas import ConversationMessage, InteractiveRequest
import validation_agent
from validation_agent import determine_next_question, extract_user_stack, has_enough_info, validate_interactive


def test_redis_is_not_enough_as_primary_database():
    conversation = [
        ConversationMessage(role="user", content="node"),
        ConversationMessage(role="assistant", content="What about the frontend?"),
        ConversationMessage(role="user", content="next"),
        ConversationMessage(role="assistant", content="For the database?"),
        ConversationMessage(role="user", content="redis"),
    ]

    stack = extract_user_stack(conversation)

    assert stack.backend == "Node.js"
    assert stack.frontend == "Next.js"
    assert stack.database == "Redis"
    assert not has_enough_info(stack)

    question = determine_next_question("build a web app", stack, "")

    assert "primary database" in question
    assert "PostgreSQL" in question


def test_persistent_database_after_redis_completes_core_stack():
    conversation = [
        ConversationMessage(role="user", content="node"),
        ConversationMessage(role="user", content="next"),
        ConversationMessage(role="user", content="redis"),
        ConversationMessage(role="user", content="postgres"),
    ]

    stack = extract_user_stack(conversation)

    assert stack.database == "PostgreSQL"
    assert has_enough_info(stack)


def test_chatbot_prompt_infers_existing_stack_and_asks_only_ai_gap(monkeypatch):
    request = InteractiveRequest(
        prompt="Build a FastAPI + React chatbot using PostgreSQL on AWS",
        conversation=[],
    )

    response = validate_interactive(request)

    assert response.status == "collecting_info"
    assert response.current_question is not None
    assert "LLM provider" in response.current_question or "memory" in response.current_question
    assert "backend" not in response.current_question.lower()
    assert "frontend" not in response.current_question.lower()
    assert "database" not in response.current_question.lower()
    assert "deployment" not in response.current_question.lower()
    assert "FastAPI" in response.context
    assert "React" in response.context
    assert "PostgreSQL" in response.context
    assert "AWS" in response.context


def test_jira_saas_prompt_finalizes_without_redundant_stack_questions(monkeypatch):
    monkeypatch.setattr(
        validation_agent,
        "get_llm_response",
        lambda _prompt: '{"project_type":"SaaS","complexity":"advanced","alignment_score":92,"missing_requirements":[],"recommended_stack":{"backend":["FastAPI"],"frontend":["React"],"database":["PostgreSQL"],"devops":["Docker"]},"feedback":"Looks complete","reasoning":"All core requirements are already provided."}',
    )

    request = InteractiveRequest(
        prompt="Build a Jira SaaS with FastAPI backend, React frontend, PostgreSQL database, AWS deployment, and WebSocket realtime updates",
        conversation=[],
    )

    response = validate_interactive(request)

    assert response.status == "success"
    assert response.current_question is None
    assert response.project_type == "SaaS"
    assert response.user_stack is not None
    assert response.user_stack.backend == "FastAPI"
    assert response.user_stack.frontend == "React"
    assert response.user_stack.database == "PostgreSQL"
    assert response.user_stack.deployment == "AWS"
    assert response.user_stack.realtime == "WebSocket"


def test_food_delivery_prompt_asks_only_for_missing_realtime(monkeypatch):
    request = InteractiveRequest(
        prompt="Build a food delivery app with Node.js backend, Vue frontend, MongoDB, and GCP deployment",
        conversation=[],
    )

    response = validate_interactive(request)

    assert response.status == "collecting_info"
    assert response.current_question is not None
    assert "real-time" in response.current_question.lower()
    assert "backend" not in response.current_question.lower()
    assert "frontend" not in response.current_question.lower()
    assert "database" not in response.current_question.lower()
    assert "deployment" not in response.current_question.lower()
    assert "Node.js" in response.context
    assert "Vue" in response.context
    assert "MongoDB" in response.context
    assert "GCP" in response.context


def test_spring_answer_confirms_backend_without_reasking_backend(monkeypatch):
    monkeypatch.setattr(
        validation_agent,
        "get_llm_response",
        lambda _prompt: '{"project_type":"mobile app","complexity":"intermediate","alignment_score":90,"missing_requirements":[],"recommended_stack":{"backend":["Spring"],"frontend":["Flutter"],"database":["MongoDB"],"devops":["Docker"]},"feedback":"Complete","reasoning":"All slots are present."}',
    )

    request = InteractiveRequest(
        prompt="Build a gaming mobile app with Flutter frontend, MongoDB database, AWS deployment, and WebSocket realtime updates",
        conversation=[
            ConversationMessage(role="assistant", content="What backend framework are you thinking of using?"),
            ConversationMessage(role="user", content="Spring"),
        ],
    )

    response = validate_interactive(request)

    assert response.status == "success"
    assert response.user_stack is not None
    assert response.user_stack.backend == "Spring"
    assert response.user_stack.frontend == "Flutter"
    assert response.user_stack.database == "MongoDB"


def test_flutter_answer_confirms_frontend_without_reasking_frontend(monkeypatch):
    monkeypatch.setattr(
        validation_agent,
        "get_llm_response",
        lambda _prompt: '{"project_type":"web app","complexity":"intermediate","alignment_score":90,"missing_requirements":[],"recommended_stack":{"backend":["Spring"],"frontend":["Flutter"],"database":["MongoDB"],"devops":["Docker"]},"feedback":"Complete","reasoning":"All slots are present."}',
    )

    request = InteractiveRequest(
        prompt="Build a gaming app with Spring backend, MongoDB database, AWS deployment, and WebSocket realtime updates",
        conversation=[
            ConversationMessage(role="assistant", content="What frontend framework are you thinking of using?"),
            ConversationMessage(role="user", content="Flutter"),
        ],
    )

    response = validate_interactive(request)

    assert response.status == "success"
    assert response.user_stack is not None
    assert response.user_stack.frontend == "Flutter"
    assert response.user_stack.backend == "Spring"
    assert response.user_stack.database == "MongoDB"


def test_mongodb_answer_confirms_database_without_reasking_database(monkeypatch):
    monkeypatch.setattr(
        validation_agent,
        "get_llm_response",
        lambda _prompt: '{"project_type":"web app","complexity":"intermediate","alignment_score":90,"missing_requirements":[],"recommended_stack":{"backend":["Spring"],"frontend":["Flutter"],"database":["MongoDB"],"devops":["Docker"]},"feedback":"Complete","reasoning":"All slots are present."}',
    )

    request = InteractiveRequest(
        prompt="Build a mobile app with Spring backend, Flutter frontend, AWS deployment, and WebSocket realtime updates",
        conversation=[
            ConversationMessage(role="assistant", content="For the database, what are you thinking?"),
            ConversationMessage(role="user", content="MongoDB"),
        ],
    )

    response = validate_interactive(request)

    assert response.status == "success"
    assert response.user_stack is not None
    assert response.user_stack.database == "MongoDB"
    assert response.user_stack.backend == "Spring"
    assert response.user_stack.frontend == "Flutter"
