"""Utility functions for Celery operations."""
{% if cookiecutter.enable_celery == "True" %}
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar, cast

from celery import Task, current_task
from celery.result import AsyncResult

from {{cookiecutter.project_name}}.celery import celery_app

T = TypeVar("T", bound=Task)


def create_periodic_task(
    name: str,
    task: str,
    schedule: Any,
    args: Optional[List[Any]] = None,
    kwargs: Optional[Dict[str, Any]] = None,
    enabled: bool = True,
) -> None:
    """
    Adds or updates a periodic task in the Celery beat schedule.

    Args:
        name: Name of the periodic task
        task: Task name to execute
        schedule: Schedule (crontab or integer in seconds)
        args: Positional arguments to pass to the task
        kwargs: Keyword arguments to pass to the task
        enabled: Whether the task is enabled
    """
    beat = celery_app.conf.beat_schedule or {}
    beat[name] = {
        "task": task,
        "schedule": schedule,
        "args": args or [],
        "kwargs": kwargs or {},
        "options": {"enabled": enabled},
    }
    celery_app.conf.beat_schedule = beat


def get_task_progress() -> Optional[Dict[str, Any]]:
    """Retrieve progress metadata for the current task."""
    if current_task and current_task.request.id:
        info = AsyncResult(current_task.request.id).info
        return cast(Dict[str, Any], info) if isinstance(info, dict) else None
    return None


def update_task_progress(
    current: int,
    total: int,
    status: str = "PROGRESS",
    **extra: Any,
) -> None:
    """Updates the current task's progress metadata.
    
    This must be called from within a task that has bind=True set.
    
    Args:
        current: Current progress value
        total: Total number of items to process
        status: Status string (e.g., "PROGRESS", "STARTED", etc.)
        **extra: Additional metadata to include in the progress update
    """
    if current_task:
        # Calculate percentage completion
        percent = int((current / total) * 100) if total > 0 else 0
        
        # Create progress metadata
        meta = {
            "current": current,
            "total": total,
            "percent": percent,
            "status": status,
            **extra,
        }
        
        # Use update_state which is the correct way to update task state
        current_task.update_state(
            state=status,
            meta=meta,
        )


def retry_on_exception(
    max_retries: int = 3,
    countdown: int = 60,
    exceptions: Optional[List[Type[Exception]]] = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Decorator for bound tasks to retry on specified exceptions.

    This decorator must be applied AFTER the @celery_app.task decorator.
    The task must be bound (use bind=True in the task decorator).

    Args:
        max_retries: Maximum number of retries
        countdown: Delay between retries in seconds
        exceptions: List of exception types to catch and retry on

    Returns:
        Decorator function
    """
    exceptions = exceptions or [Exception]

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        def wrapper(self: Task, *args: Any, **kwargs: Any) -> Any:
            try:
                return func(self, *args, **kwargs)
            except tuple(exceptions) as exc:
                if self.request.retries >= max_retries:
                    raise
                # raise to ensure Celery handles scheduling
                return self.retry(countdown=countdown, exc=exc)

        return wrapper

    return decorator
{% endif %} 