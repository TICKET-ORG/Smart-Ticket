from fastapi import APIRouter, HTTPException, Request

from app.config import settings
from app.web.deps import RepositoryDep
from app.web.templating import render

router = APIRouter(tags=["frontend"])


@router.get("/", include_in_schema=False)
def landing_page(request: Request, repository: RepositoryDep):
    return render(
        request,
        "public/landing.html",
        {
            "events": repository.featured_events(limit=3),
            "hero_event": repository.get_event("evt-senja-kala"),
            "active_page": "home",
        },
    )


@router.get("/dev/styleguide", include_in_schema=False)
def styleguide_page(request: Request, repository: RepositoryDep):
    if settings.is_production:
        raise HTTPException(status_code=404, detail="Not found")

    return render(
        request,
        "dev/styleguide.html",
        {
            "events": repository.featured_events(limit=2),
            "logs": repository.list_checkin_logs(limit=3),
            "active_page": "styleguide",
        },
    )
