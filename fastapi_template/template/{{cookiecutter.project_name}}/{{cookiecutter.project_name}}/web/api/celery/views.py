"""API endpoints for Celery task management."""
{% if cookiecutter.enable_celery == "True" %}
from typing import Any, Dict, List

from celery.exceptions import NotRegistered
from fastapi import APIRouter, Depends, HTTPException, Query

{% if cookiecutter.enable_loguru == "True" %}
from {{cookiecutter.project_name}}.log import logger
{% endif %}
from {{cookiecutter.project_name}}.services.celery.dependencies import get_celery_manager
from {{cookiecutter.project_name}}.services.celery.manager import CeleryManager

router = APIRouter(prefix="/celery", tags=["Celery"])


@router.get("/simple")
async def run_simple_task(
    name: str = Query(default="test_user", description="Name to greet"),
    celery_manager: CeleryManager = Depends(get_celery_manager),
) -> Dict[str, str]:
    """Fire off the simple example_task which just returns a greeting."""
    try:
        result = celery_manager.execute_task(
            task_name="example_task",
            kwargs={"name": name},
        )
        return {"task_id": result.id}
    except NotRegistered:
        # Get tasks registered in both app and workers for better diagnostics
        app_tasks = celery_manager.get_registered_tasks()
        worker_tasks = celery_manager.get_worker_registered_tasks()
        
        raise HTTPException(
            status_code=400,
            detail=(
                "example_task is not registered. "
                f"App knows about: {app_tasks}. "
                f"Worker knows about: {worker_tasks}. "
                "Ensure task modules are properly imported in both the app and worker."
            ),
        )


@router.get("/long")
async def run_long_task(
    item_count: int = Query(default=3, description="Number of dummy items to process"),
    celery_manager: CeleryManager = Depends(get_celery_manager),
) -> Dict[str, str]:
    """
    Fire off the long-running example_long_task with generated dummy data.
    """
    # Generate dummy items based on count
    items = [
        {"id": f"item_{i}", "value": f"test_value_{i}"}
        for i in range(item_count)
    ]
    
    try:
        result = celery_manager.execute_task(
            task_name="example_long_task",
            kwargs={"items": items},
        )
        return {"task_id": result.id}
    except NotRegistered:
        # Get tasks registered in both app and workers for better diagnostics
        app_tasks = celery_manager.get_registered_tasks()
        worker_tasks = celery_manager.get_worker_registered_tasks()
        
        raise HTTPException(
            status_code=400,
            detail=(
                "example_long_task is not registered. "
                f"App knows about: {app_tasks}. "
                f"Worker knows about: {worker_tasks}. "
                "Ensure task modules are properly imported in both the app and worker."
            ),
        )


@router.get("/retry")
async def run_retry_task(
    should_fail: bool = Query(default=False, description="Set to true to test failure/retry"),
    celery_manager: CeleryManager = Depends(get_celery_manager),
) -> Dict[str, str]:
    """
    Fire off the example_retry_task, which demonstrates automatic retry.
    """
    # Choose URL based on whether we want to test the success or failure case
    url = "https://example.com/fail" if should_fail else "https://example.com"
    
    try:
        result = celery_manager.execute_task(
            task_name="example_retry_task",
            kwargs={"url": url},
        )
        return {"task_id": result.id}
    except NotRegistered:
        # Get tasks registered in both app and workers for better diagnostics
        app_tasks = celery_manager.get_registered_tasks()
        worker_tasks = celery_manager.get_worker_registered_tasks()
        
        raise HTTPException(
            status_code=400,
            detail=(
                "example_retry_task is not registered. "
                f"App knows about: {app_tasks}. "
                f"Worker knows about: {worker_tasks}. "
                "Ensure task modules are properly imported in both the app and worker."
            ),
        )


@router.get("/status/{task_id}")
async def get_task_status(
    task_id: str,
    celery_manager: CeleryManager = Depends(get_celery_manager),
) -> Dict[str, Any]:
    """
    Poll the state (and result or error) of any task by its ID.
    """
    status = celery_manager.get_status(task_id)
    return status


@router.get("/tasks")
async def list_all_tasks(
    celery_manager: CeleryManager = Depends(get_celery_manager),
) -> Dict[str, Any]:
    """
    List all tasks registered in both the app and workers.
    """
    return {
        "app_tasks": celery_manager.get_registered_tasks(),
        "worker_tasks": celery_manager.get_worker_registered_tasks(),
        "are_in_sync": celery_manager.get_registered_tasks() == celery_manager.get_worker_registered_tasks()
    }
{% endif %} 