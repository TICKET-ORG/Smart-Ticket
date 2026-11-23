"""Account screens.

The forms are presentation only until the backend session layer exists: a POST
renders the same page with a demo notice instead of authenticating anyone.
"""

from fastapi import APIRouter, Request

from app.web.templating import render

router = APIRouter(prefix="/auth", tags=["auth"])

DEMO_NOTICE = "Demo mode — accounts are not connected yet. Nothing was submitted or saved."


@router.get("/login")
def login_page(request: Request, next: str = ""):
    return render(
        request,
        "public/login.html",
        {"active_page": "login", "next": next},
    )


@router.post("/login")
async def login_submit(request: Request, next: str = ""):
    form = await request.form()

    return render(
        request,
        "public/login.html",
        {
            "active_page": "login",
            "next": next,
            "form_email": str(form.get("email", "")),
            "notice": DEMO_NOTICE,
        },
    )


@router.get("/register")
def register_page(request: Request, next: str = ""):
    return render(
        request,
        "public/register.html",
        {"active_page": "register", "next": next},
    )


@router.post("/register")
async def register_submit(request: Request, next: str = ""):
    form = await request.form()

    return render(
        request,
        "public/register.html",
        {
            "active_page": "register",
            "next": next,
            "form_name": str(form.get("name", "")),
            "form_email": str(form.get("email", "")),
            "notice": DEMO_NOTICE,
        },
    )
