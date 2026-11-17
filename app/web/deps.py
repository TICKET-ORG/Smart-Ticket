from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from app.mock.repository import DemoRepository


@lru_cache(maxsize=1)
def _demo_repository() -> DemoRepository:
    return DemoRepository()


def get_repository() -> DemoRepository:
    """Return the active data repository.

    Only demo data exists today. When the backend lands, this dependency will
    select the database-backed repository without touching page routes.
    """

    return _demo_repository()


RepositoryDep = Annotated[DemoRepository, Depends(get_repository)]
