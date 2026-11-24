"""Shared guard for interface-only routes.

These routes have no session check yet, so they must not be reachable in a
non-demo deployment. Replace the call with a real session dependency when auth
lands; do not relax the guard in the meantime.
"""

from __future__ import annotations

from fastapi import HTTPException

from app.config import settings


def require_demo() -> None:
    if not settings.demo_mode:
        raise HTTPException(status_code=404, detail="Not found")
