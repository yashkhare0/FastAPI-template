from fastapi.routing import APIRouter

{%- if cookiecutter.add_users == 'True' %}
from {{cookiecutter.project_name}}.web.api import users
from {{cookiecutter.project_name}}.db.models.users import api_users
{%- endif %}
{%- if cookiecutter.enable_routers == "True" %}
{%- if cookiecutter.api_type == 'rest' %}
from {{cookiecutter.project_name}}.web.api import echo

{%- if cookiecutter.add_dummy == 'True' %}
from {{cookiecutter.project_name}}.web.api import dummy

{%- endif %}
{%- if cookiecutter.enable_redis == "True" %}
from {{cookiecutter.project_name}}.web.api import redis

{%- endif %}
{%- if cookiecutter.enable_rmq == "True" %}
from {{cookiecutter.project_name}}.web.api import rabbit

{%- endif %}
{%- if cookiecutter.enable_kafka == "True" %}
from {{cookiecutter.project_name}}.web.api import kafka

{%- endif %}
{%- if cookiecutter.enable_celery == "True" %}
from {{cookiecutter.project_name}}.web.api import celery

{%- endif %}
{%- endif %}
{%- endif %}
{%- if cookiecutter.self_hosted_swagger == "True" %}
from {{cookiecutter.project_name}}.web.api import docs

{%- endif %}
from {{cookiecutter.project_name}}.web.api import monitoring

api_router = APIRouter()
api_router.include_router(monitoring.router)
{%- if cookiecutter.add_users == 'True' %}
api_router.include_router(users.router)
{%- endif %}
{%- if cookiecutter.self_hosted_swagger == "True" %}
api_router.include_router(docs.router)
{%- endif %}
{%- if cookiecutter.enable_routers == "True" %}
{%- if cookiecutter.api_type == 'rest' %}
api_router.include_router(echo.router, prefix="/echo", tags=["echo"])
{%- if cookiecutter.add_dummy == 'True' %}
api_router.include_router(dummy.router, prefix="/dummy", tags=["dummy"])
{%- endif %}
{%- if cookiecutter.enable_redis == "True" %}
api_router.include_router(redis.router, prefix="/redis", tags=["redis"])
{%- endif %}
{%- if cookiecutter.enable_rmq == "True" %}
api_router.include_router(rabbit.router, prefix="/rabbit", tags=["rabbit"])
{%- endif %}
{%- if cookiecutter.enable_kafka == "True" %}
api_router.include_router(kafka.router, prefix="/kafka", tags=["kafka"])
{%- endif %}
{%- if cookiecutter.enable_celery == "True" %}
api_router.include_router(celery.router, prefix="/celery", tags=["celery"])
{%- endif %}
{%- endif %}
{%- endif %}
