"""Celery task manager module."""
{% if cookiecutter.enable_celery == "True" %}
from typing import Any, Dict, List, Optional, Set

from celery import Celery
from celery.exceptions import NotRegistered
from celery.result import AsyncResult

from {{cookiecutter.project_name}}.celery import celery_app


class CeleryManager:
    """Provides methods to execute Celery tasks and inspect worker state."""

    def __init__(self, app: Celery) -> None:
        """
        Initialize the manager with a Celery app instance.

        :param app: Instance of celery.Celery
        """
        self._app = app

    @property
    def inspector(self) -> Any:
        """Return celery inspector."""
        return self._app.control.inspect()

    def execute_task(
        self,
        task_name: str,
        args: Optional[List[Any]] = None,
        kwargs: Optional[Dict[str, Any]] = None,
        **options: Any,
    ) -> AsyncResult:
        """
        Execute a Celery task.

        :param task_name: Name of the task to execute
        :param args: Positional arguments for the task
        :param kwargs: Keyword arguments for the task
        :param options: Additional options (countdown, expires, retry, etc.)
        :return: AsyncResult object for the task
        """
        return self.submit_task(name=task_name, args=args, kwargs=kwargs, **options)
    
    def submit_task(
        self,
        name: str,
        args: Optional[List[Any]] = None,
        kwargs: Optional[Dict[str, Any]] = None,
        **options: Any,
    ) -> AsyncResult:
        """
        Submit a task by name.

        :param name: Registered task name.
        :param args: Positional arguments for the task.
        :param kwargs: Keyword arguments for the task.
        :param options: Additional apply_async options
        :return: AsyncResult instance.
        """
        task = self._app.tasks[name]
        return task.apply_async(args=args or [], kwargs=kwargs or {}, **options)

    def get_status(self, task_id: str) -> Dict[str, Any]:
        """
        Fetch the state and result (or error) of a task.

        :param task_id: UUID of the task.
        :return: Dictionary with task metadata.
        """
        try:
            result = AsyncResult(task_id, app=self._app)
            data: Dict[str, Any] = {
                "id": task_id,
                "state": result.state,
                "ready": result.ready(),
                "success": result.successful(),
                "failure": result.failed(),
            }
            if result.ready():
                key = "result" if result.successful() else "error"
                data[key] = result.result
            return data
        except NotRegistered as e:
            # Handle the case where the task exists in the result backend
            # but the task type is not registered in this worker
            return {
                "id": task_id,
                "state": "UNKNOWN",
                "ready": False,
                "success": False,
                "failure": True,
                "error": f"Task type not registered: {str(e)}",
            }
        except Exception as e:
            # Handle other exceptions that might occur when retrieving status
            return {
                "id": task_id,
                "state": "ERROR",
                "ready": False,
                "success": False,
                "failure": True,
                "error": f"Error retrieving task status: {str(e)}",
            }

    def list_tasks(self) -> List[str]:
        """
        List all registered task names in the app.

        :return: List of task name strings.
        """
        return list(self._app.tasks.keys())

    def get_worker_tasks(self) -> Set[str]:
        """
        Get the set of tasks registered with workers.
        
        :return: Set of task names registered with at least one worker
        """
        worker_registered = self.registered()
        worker_tasks = set()
        
        # Collect all tasks registered on any worker
        for worker_name, tasks in worker_registered.items():
            worker_tasks.update(tasks)
            
        return worker_tasks
    
    def get_registered_tasks(self) -> str:
        """
        Get a formatted string of user-defined registered tasks.

        :return: Formatted string of task names
        """
        all_tasks = self.list_tasks()
        # Filter out internal Celery tasks
        user_tasks = [
            task for task in all_tasks
            if not task.startswith("celery.") and not task.startswith("__")
        ]
        # Sort tasks for consistent output
        user_tasks.sort()
        # Format the output for display in error messages
        if user_tasks:
            return ", ".join(user_tasks)
        return "No user-defined tasks found"

    def get_worker_registered_tasks(self) -> str:
        """
        Get a formatted string of tasks registered with workers.
        
        :return: Formatted string of task names
        """
        worker_tasks = self.get_worker_tasks()
        
        # Filter out internal Celery tasks
        user_worker_tasks = [
            task for task in worker_tasks
            if not task.startswith("celery.") and not task.startswith("__")
        ]
        
        # Sort tasks for consistent output
        user_worker_tasks = sorted(user_worker_tasks)
        
        # Format the output for display in error messages
        if user_worker_tasks:
            return ", ".join(user_worker_tasks)
        return "No user-defined tasks found on workers"

    def registered(self) -> Dict[str, Any]:
        """Return registered task names per worker."""
        return self.inspector.registered() or {}


# Default manager using the application's Celery instance
default_manager = CeleryManager(celery_app)
{% endif %} 