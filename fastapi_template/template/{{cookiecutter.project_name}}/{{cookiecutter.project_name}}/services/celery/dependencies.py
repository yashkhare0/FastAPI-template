"""Celery dependency providers."""
{% if cookiecutter.enable_celery == "True" %}
from fastapi import Depends

from {{cookiecutter.project_name}}.services.celery.manager import CeleryManager, default_manager


def get_celery_manager() -> CeleryManager:
    """
    Returns the default CeleryManager.
    
    This is used as a FastAPI dependency to provide the manager
    to API endpoints.
    """
    return default_manager
{% endif %} 