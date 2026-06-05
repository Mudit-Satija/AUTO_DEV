import asyncio
import logging
import math
import os
from typing import Any, Callable, Dict, Tuple

logger = logging.getLogger(__name__)

# Configurable via environment
MAX_RETRIES = int(os.getenv("RELIABILITY_MAX_RETRIES", "3"))
INITIAL_BACKOFF = float(os.getenv("RELIABILITY_INITIAL_BACKOFF", "0.5"))

# Simple in-memory metrics
metrics = {
    "agent_success": {},
    "agent_retries": {},
    "agent_fallbacks": {},
    "validation_failures": {},
}


def _inc(counter: str, agent: str, by: int = 1):
    metrics.setdefault(counter, {})
    metrics[counter].setdefault(agent, 0)
    metrics[counter][agent] += by


def validate_schema(agent_name: str, result: Any, required_fields: Tuple[str, ...]) -> Tuple[bool, list]:
    """Basic schema validator: ensures result is dict and has required keys."""
    errors = []
    if not isinstance(result, dict):
        errors.append("not a dict")
        return False, errors
    for key in required_fields:
        if key not in result:
            errors.append(f"missing field: {key}")
    return (len(errors) == 0), errors


async def call_with_retries(
    coro_func: Callable[[], Any],
    agent_name: str,
    required_fields: Tuple[str, ...],
    fallback_func: Callable[[], Any],
    max_retries: int = None,
    initial_backoff: float = None,
) -> Any:
    """Call an async agent function with retries, validation and fallback.

    coro_func: zero-arg callable that returns awaitable
    fallback_func: zero-arg callable returning fallback value
    """
    if max_retries is None:
        max_retries = MAX_RETRIES
    if initial_backoff is None:
        initial_backoff = INITIAL_BACKOFF

    attempt = 0
    backoff = initial_backoff
    last_exception = None

    logger.info(f"[AGENT START] {agent_name}")

    while attempt <= max_retries:
        try:
            attempt += 1
            if attempt > 1:
                logger.info(f"[RETRY] {agent_name} attempt {attempt}")
                _inc("agent_retries", agent_name)

            result = await coro_func()

            valid, errors = validate_schema(agent_name, result, required_fields)
            if not valid:
                _inc("validation_failures", agent_name)
                logger.warning(f"[VALIDATION FAILED] {agent_name} attempt {attempt}: {errors}")
                last_exception = Exception("Validation failed: " + ",".join(errors))
                # decide to retry if attempts left
                if attempt <= max_retries:
                    await asyncio.sleep(backoff)
                    backoff *= 2
                    continue
                else:
                    break

            logger.info(f"[AGENT SUCCESS] {agent_name}")
            _inc("agent_success", agent_name)
            return result

        except asyncio.CancelledError:
            logger.error(f"[AGENT FAILED] {agent_name} cancelled")
            last_exception = None
            raise
        except Exception as e:
            last_exception = e
            logger.warning(f"[AGENT FAILED] {agent_name} attempt {attempt}: {type(e).__name__}: {e}")
            if attempt <= max_retries:
                await asyncio.sleep(backoff)
                backoff *= 2
                continue
            else:
                break

    # exhausted retries -> use fallback
    logger.error(f"[FALLBACK USED] {agent_name} after {attempt} attempts")
    _inc("agent_fallbacks", agent_name)
    try:
        fb = fallback_func()
        logger.info(f"[PIPELINE CONTINUED] {agent_name} used fallback")
        return fb
    except Exception as e:
        logger.error(f"[FALLBACK FAILED] {agent_name}: {e}")
        raise last_exception if last_exception else e


def get_metrics():
    return metrics
