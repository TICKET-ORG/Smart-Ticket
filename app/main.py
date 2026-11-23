from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.config import BASE_DIR, settings
from app.web.routes import auth, events, frontend
from app.web.templating import render


def create_app() -> FastAPI:
    application = FastAPI(
        title=settings.app_name,
        description="Frontend for the Smart Event Ticketing System.",
        version="0.1.0",
        docs_url="/api/docs" if settings.app_debug else None,
        redoc_url=None,
    )

    application.mount(
        "/static",
        StaticFiles(directory=str(BASE_DIR / "app" / "static")),
        name="static",
    )

    application.include_router(frontend.router)
    application.include_router(events.router)
    application.include_router(auth.router)

    @application.get("/healthz", include_in_schema=False)
    def healthz() -> dict[str, str | bool]:
        return {"status": "ok", "demo_mode": settings.demo_mode}

    @application.exception_handler(404)
    async def not_found(request: Request, _exc: Exception):
        if request.url.path.startswith("/api/"):
            return JSONResponse({"detail": "Not found"}, status_code=404)
        return render(request, "errors/404.html", status_code=404)

    return application


app = create_app()
