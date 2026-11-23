from datetime import date, datetime
from typing import Any

from fastapi import Request
from fastapi.templating import Jinja2Templates

from app.config import BASE_DIR, settings
from app.web.navigation import DEMO_ROLES, nav_for, role_label

templates = Jinja2Templates(directory=str(BASE_DIR / "app" / "templates"))

templates.env.globals["nav_for"] = nav_for
templates.env.globals["role_label"] = role_label


def _strftime(value: datetime | date | None, fmt: str) -> str:
    if value is None:
        return ""
    return value.strftime(fmt)


templates.env.filters["date"] = _strftime
templates.env.filters["date_short"] = lambda value: _strftime(value, "%a, %d %b")
templates.env.filters["date_long"] = lambda value: _strftime(value, "%A, %d %B %Y")
templates.env.filters["time"] = lambda value: _strftime(value, "%H:%M")


def render(
    request: Request,
    template_name: str,
    context: dict[str, Any] | None = None,
    *,
    status_code: int = 200,
) -> Any:
    """Render a template with the globals every page expects."""

    payload: dict[str, Any] = {
        "app_name": settings.app_name,
        "current_user": None,
        "current_year": date.today().year,
        "demo_mode": settings.demo_mode,
        "active_page": None,
        "nav_role": None,
        "page_title": None,
        "page_kicker": None,
        "demo_roles": DEMO_ROLES,
    }
    if context:
        payload.update(context)

    return templates.TemplateResponse(
        request=request,
        name=template_name,
        context=payload,
        status_code=status_code,
    )
