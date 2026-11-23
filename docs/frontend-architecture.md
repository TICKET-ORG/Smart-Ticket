# Frontend architecture

## Goal

Ship the interface for a face-verified ticketing system without inventing a
parallel backend. Pages are server-rendered by FastAPI and Jinja2, and the same
routes will later render live data from the application services.

## Layers

| Layer | Location | Responsibility |
| --- | --- | --- |
| Page controllers | `app/web/routes/` | Parse request, call the repository, choose a template and status code |
| View helpers | `app/web/templating.py` | Shared render context, date filters |
| Data dependency | `app/web/deps.py` | One seam that selects demo or live data |
| Demo data | `app/mock/` | Fixtures and an in-memory repository |
| Presentation | `app/templates/` | Semantic HTML and reusable macros |
| Behaviour | `app/static/js/` | Camera, forms, navigation; no framework |
| Visual system | `app/static/css/` | Tokens first, then layout, components, page overrides |

Controllers stay thin. Templates do not import fixtures, query data, or format
business logic. Formatting that is shared belongs in model properties (for
example `event.capacity_pct`) or in a presenter helper, not inline Jinja.

## Request flow

```
Browser
  └─ GET /
       └─ frontend.landing_page
            ├─ RepositoryDep → DemoRepository
            └─ render("public/landing.html", context)
                 └─ base.html → components → page blocks
```

## Application shell

Public pages extend `base.html`. Signed-in pages extend `base_app.html`, which
overrides the `shell` block and adds a paper sidebar, a sticky topbar, and the
accent demo strip. Sidebar items come from `app/web/navigation.py`; the role
switcher reads `DEMO_ROLES` and marks roles without routes as disabled so the
demo never links to a missing page.

The mobile sidebar is a small state machine in `core/app-shell.js`
(`data-sidebar-open` on the shell, scrim click and Escape close, focus returns
to the toggle). Page controllers pass `nav_role`, `page_title`, `page_kicker`,
and `active_page`; `templating.py` supplies empty defaults for public pages.

## Data contract

`DemoEvent`, `DemoTicket`, `DemoUser`, `DemoFaceProfile`, `DemoRegistration`, and
`DemoCheckinLog` mirror the field names used by the backend ORM. Ticket and
registration views (`DemoTicketView`, `DemoRegistrationView`) are the joined
shapes pages render; they mirror ORM relationships rather than duplicating
columns. Keep that invariant: if the backend adds `Event.slug`, add it to the
fixture too rather than renaming it in the template.

The repository currently exposes:

```python
list_events(limit=None)
featured_events(limit=3)
get_event(event_id)
list_categories()
search_events(query="", category="")
related_events(event_id, limit=3)
user_for_role(role)
get_user(user_id)
face_profile_for(user_id)
list_tickets_for(user_id)
ticket_by_id(ticket_id)
ticket_view(ticket_id)
list_ticket_views_for(user_id)
next_ticket_for(user_id)
list_registrations_for(user_id)
list_registration_views_for(user_id)
list_checkin_logs(limit=None)
```

Add methods only when a page needs them. The live implementation should satisfy
the same signatures.

## Integration seam

`app/web/deps.py` is the only place that knows where data comes from:

```python
def get_repository() -> DemoRepository:
    return _demo_repository()
```

Replace the return value with a database-backed repository when the backend is
merged. Routes keep depending on `RepositoryDep`. Do not branch on
`DEMO_MODE` inside templates or page functions.

Interactive endpoints (enrollment sample upload, scanner validation) will get a
temporary mock router in `app/mock/` during their PRs, registered only when
`DEMO_MODE=true`. The real backend router replaces that registration without
changes to the JavaScript callers.

## Routes

Implemented (`frontend`, `events`, `auth`, `participant` routers):

| Route | Notes |
| --- | --- |
| `/` | Landing page |
| `/events` | Catalog with `q` and `category` query params |
| `/events/{id}` | Detail; unknown ids fall through to the designed 404 |
| `/auth/login`, `/auth/register` | Presentation only; POST re-renders with a demo notice |
| `/participant/dashboard` | Participant overview; demo-only guard |
| `/participant/enrollment` | Camera capture UI; frames never leave the page |
| `/participant/tickets` | Pass list for the demo account |
| `/participant/tickets/{id}` | Pass sheet; other users' ids return 404 |
| `/participant/tickets/{id}/qr.png` | QR image generated from the demo token |

Participant routes call `_guard_demo()` and return 404 when `DEMO_MODE=false`.
Replace that guard with the real session dependency once auth lands; do not
remove it while the demo account is the only source of identity.

Planned:

| Area | Planned routes |
| --- | --- |
| Auth | `/auth/logout` |
| Operator | `/operator/dashboard`, `/operator/scanner`, `/operator/history` |
| Admin | `/admin/dashboard`, `/admin/events`, `/admin/registrations`, `/admin/operators`, `/admin/analytics`, `/admin/model` |
| Lab | `/cv-lab`, `/research/results` |
| Dev | `/dev/styleguide` (404 in production) |

## JavaScript

Use ES modules and `type="module"` scripts. Each module exports an `init…`
function and is imported from `app/static/js/app.js` or a page-level script.
Keep DOM queries scoped to the component; no global jQuery-style helpers.

Current modules: `core/nav.js` (public mobile menu), `core/app-shell.js`
(sidebar and role switcher), and `pages/enrollment.js` (camera and pose
capture). The enrollment module is self-initializing because it is loaded only
by its page.

Camera modules must handle permission denial, missing devices, and stream
cleanup. Never upload a frame silently: show the session state and the result.
The enrollment page draws frames to a local canvas, keeps them as data URLs in
the DOM, and stops tracks on `pagehide`.

## CSS

Load order is fixed: `tokens.css`, `base.css`, `layout.css`, `components.css`,
then one optional page stylesheet. Page CSS may extend components but must not
redefine tokens. Use BEM-ish class names and data attributes for state.

## Testing

`pytest` smoke tests render every page, check demo-mode gating, and touch the
main static assets. `tests/test_participant.py` covers the pass joins, the
unknown-ticket 404, and the PNG response. Add tests when a route gains branching
behaviour. Browser automation is reserved for the enrollment and scanner flows,
where a camera mock is required; the capture UI has been checked with Chrome's
fake media stream and must stay free of non-GET requests.

## Conventions

- Conventional Commits: `feat(scope): …`, `fix(scope): …`, `docs: …`,
  `chore: …`.
- One concern per commit; keep the demo data layer separate from UI commits.
- No biometric assets or secrets in git.
- Every new page needs an empty state, an error state, and a mobile check.