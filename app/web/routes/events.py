from fastapi import APIRouter, HTTPException, Request

from app.web.deps import RepositoryDep
from app.web.templating import render

router = APIRouter(tags=["events"])


@router.get("/events")
def event_catalog(
    request: Request,
    repository: RepositoryDep,
    q: str = "",
    category: str = "",
):
    events = repository.search_events(query=q, category=category)

    return render(
        request,
        "public/events.html",
        {
            "events": events,
            "categories": repository.list_categories(),
            "query": q,
            "category": category,
            "total_events": len(repository.list_events()),
            "active_page": "events",
        },
    )


@router.get("/events/{event_id}")
def event_details(request: Request, event_id: str, repository: RepositoryDep):
    event = repository.get_event(event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")

    return render(
        request,
        "public/event_details.html",
        {
            "event": event,
            "related": repository.related_events(event_id),
            "active_page": "events",
        },
    )
