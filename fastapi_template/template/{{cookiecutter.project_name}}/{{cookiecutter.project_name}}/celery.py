"""Celery application configuration."""
{% if cookiecutter.enable_celery == "True" %}
from celery import Celery

# Configure the Celery instance
celery_app = Celery(
    "{{cookiecutter.project_name}}",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0",
    include=["{{cookiecutter.project_name}}.tasks.example"],
)

# Optional configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    enable_utc=True,
    task_track_started=True,
    worker_send_task_events=True,
    task_send_sent_event=True,
)
{% endif %} 