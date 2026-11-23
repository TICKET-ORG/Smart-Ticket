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

## Data contract

`DemoEvent`, `DemoTicket`, `DemoUser`, and `DemoCheckinLog` mirror the field
names used by the backend ORM. Keep that invariant: if the backend adds
`Event.slug`, add it to the fixture too rather than renaming it in the template.

The repository currently exposes:

```python
list_events(limit=None)
featured_events(limit=3)
get_event(event_id)
list_categories()
search_events(query="", category="")
related_events(event_id, limit=3)
user_for_role(role)
list_tickets_for(user_id)
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

Implemented (`frontend`, `events`, `auth` routers):

| Route | Notes |
| --- | --- |
| `/` | Landing page |
| `/events` | Catalog with `q` and `category` query params |
| `/events/{id}` | Detail; unknown ids fall through to the designed 404 |
| `/auth/login`, `/auth/register` | Presentation only; POST re-renders with a demo notice |

Planned:

| Area | Planned routes |
| --- | --- |
| Auth | `/auth/logout` |
| Participant | `/participant/dashboard`, `/participant/enrollment`, `/participant/tickets`, `/participant/tickets/{id}` |
| Operator | `/operator/dashboard`, `/operator/scanner`, `/operator/history` |
| Admin | `/admin/dashboard`, `/admin/events`, `/admin/registrations`, `/admin/operators`, `/admin/analytics`, `/admin/model` |
| Lab | `/cv-lab`, `/research/results` |
| Dev | `/dev/styleguide` (404 in production) |

## JavaScript

Use ES modules and `type="module"` scripts. Each module exports an `init…`
function and is imported from `app/static/js/app.js` or a page-level script.
Keep DOM queries scoped to the component; no global jQuery-style helpers.

Camera modules must handle permission denial, missing devices, and stream
cleanup. Never upload a frame silently: show the session state and the result.

## CSS

Load order is fixed: `tokens.css`, `base.css`, `layout.css`, `components.css`,
then one optional page stylesheet. Page CSS may extend components but must not
redefine tokens. Use BEM-ish class names and data attributes for state.

## Testing

`pytest` smoke tests render every page and touch the main static assets. Add
tests when a route gains branching behaviour. Browser automation is reserved for
the enrollment and scanner flows, where a camera mock is required.

## Conventions

- Conventional Commits: `feat(scope): …`, `fix(scope): …`, `docs: …`,
  `chore: …`.
- One concern per commit; keep the demo data layer separate from UI commits.
- No biometric assets or secrets in git.
- Every new page needs an empty state, an error state, and a mobile check.