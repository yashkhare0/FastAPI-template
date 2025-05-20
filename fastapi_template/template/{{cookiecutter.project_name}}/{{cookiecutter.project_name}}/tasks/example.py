"""Example tasks demonstrating Celery functionality."""
{% if cookiecutter.enable_celery == "True" %}
import time
from typing import Any, Dict, List

from {{cookiecutter.project_name}}.celery import celery_app
from {{cookiecutter.project_name}}.services.celery.utils import retry_on_exception, update_task_progress


@celery_app.task(name="example_task")
def example_task(name: str) -> str:
    """
    Example task to demonstrate Celery functionality.

    Args:
        name: Name to greet.

    Returns:
        Greeting message.
    """
    return f"Hello, {name}!"


@celery_app.task(bind=True, name="example_long_task")
def example_long_task(self: Any, items: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Example long-running task with progress reporting.

    This task demonstrates how to report progress that can be tracked by clients.

    Args:
        items: List of items to process

    Returns:
        Result summary
    """
    total = len(items)
    for i, item in enumerate(items):
        # Process the item (simulated with sleep)
        time.sleep(0.5)

        # Update progress
        update_task_progress(
            current=i + 1,
            total=total,
            status="PROGRESS",
            item_id=item.get("id"),
            description=f"Processing item {i + 1}/{total}",
        )
    return {
        "status": "COMPLETED",
        "total_processed": total,
        "message": f"Processed {total} items successfully",
    }


@celery_app.task(bind=True, name="example_retry_task")
@retry_on_exception(max_retries=3, exceptions=[ConnectionError, TimeoutError])
def example_retry_task(self: Any, url: str) -> Dict[str, Any]:
    """
    Example task that demonstrates automatic retrying on exceptions.

    Args:
        self: Task instance (injected by Celery)
        url: URL to connect to

    Returns:
        Response data
    """
    # Simulate a connection that might fail
    if url == "https://example.com/fail":
        raise ConnectionError("Failed to connect to the server")

    # Simulate successful processing
    return {
        "status": "success",
        "url": url,
        "data": {"result": "Connection successful"},
    }
{% endif %} 