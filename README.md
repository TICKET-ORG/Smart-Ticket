# SmartTicket — Smart Event Ticketing Web

Frontend for a face-verified event ticketing system. A ticket is a single-use
QR pass, and entry requires a match between the pass owner and the face at the
gate.

The recognition pipeline (HOG descriptor, K-NN matching, PSO-tuned threshold)
runs on the Python backend. This repository is being built frontend-first and
will be wired to the backend data layer as it lands.

> **Status — PR 3 / participant workspace.** The application shell, design
> system, landing page, event catalog, event detail, account screens, component
> style guide, demo data repository, and the participant workspace (overview,
> face enrollment, passes) are in place. Operator, admin, and CV lab screens are
> next.

## Frontend scope

This build is interface only. Every screen renders from demo fixtures, and
interactive flows stop at the presentation layer:

- Sign-in and registration forms validate in the browser, then re-render the
  page with a visible "demo mode" notice. No session, cookie, or account is
  created.
- Registration buttons on event pages lead to sign-in. There is no booking
  transaction.
- Participant screens render one fixed demo account. The role switcher only
  moves between implemented demo roles; roles without pages are shown disabled.
- Face enrollment asks the browser for camera access and draws nine frames to a
  local canvas so the participant can see progress. Nothing is uploaded: the
  save button reports that the endpoint is not connected.
- Face recognition is not simulated anywhere. The operator screens will show a
  real idle/scanning state and only display a verdict once the backend
  endpoint returns one.

Connecting the forms and scanner to the backend happens in a later pass, once
the API contract in `docs/integration-contract.md` is implemented.

---

## Stack

- FastAPI + Jinja2 server-rendered pages
- HTML5, CSS3 custom properties, vanilla JavaScript ES modules
- No Node.js runtime and no build step
- Fonts vendored locally (Instrument Sans / Instrument Serif, OFL)
- Demo data served from an in-memory repository while the backend is built

## Quickstart

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
./run.sh                           # Windows: .\run.ps1
```

Open <http://127.0.0.1:8000>.

Useful routes:

| Route | Purpose |
| --- | --- |
| `/` | Public landing page |
| `/events` | Event catalog with search and category filter |
| `/events/{id}` | Event detail with schedule and entry steps |
| `/auth/login`, `/auth/register` | Account screens (presentation only) |
| `/participant/dashboard` | Participant overview, next pass, enrollment state |
| `/participant/enrollment` | Guided nine-pose face capture (local only) |
| `/participant/tickets` | Every pass on the demo account |
| `/participant/tickets/{id}` | Pass sheet with QR and entry notes |
| `/participant/tickets/{id}/qr.png` | Server-rendered QR image for the pass |
| `/dev/styleguide` | Design tokens and component catalogue |
| `/healthz` | Application health check |
| `/api/docs` | OpenAPI docs (development only) |

## Demo mode

`DEMO_MODE=true` (default) makes the page routes read from
`app/mock/repository.py`. Fixtures are shaped like the backend ORM models so
templates do not need to change when the real repository replaces the demo one.

The participant routes are gated on this flag and return 404 when it is off.
There is no session guard yet, so exposing them in a non-demo deployment would
show one account's data to every visitor.

To move to live data, implement the same repository methods against the backend
and switch the dependency in `app/web/deps.py`. Do not scatter fixture imports
through routes or templates.

Copy `.env.example` to `.env` to override configuration.

## Project structure

```
app/
├── main.py                  # App factory, static mount, error handler
├── config.py                # Environment settings
├── mock/                    # Temporary demo data layer
│   ├── fixtures.py
│   └── repository.py
├── web/
│   ├── deps.py              # Repository dependency (integration seam)
│   ├── navigation.py        # Role labels, sidebar nav, demo role switcher
│   ├── enrollment.py        # Guided pose copy for the capture UI
│   ├── templating.py        # Jinja environment and render helper
│   └── routes/              # Page controllers
├── templates/
│   ├── base.html            # Public shell
│   ├── base_app.html        # Signed-in shell: sidebar, topbar, demo strip
│   ├── components/          # Navbar, footer, cards, app shell, icon macro
│   ├── public/              # Landing, catalog, event detail, account screens
│   ├── participant/         # Overview, enrollment, passes
│   ├── dev/                 # Style guide (development only)
│   └── errors/
└── static/
    ├── css/                 # tokens, base, layout, components, app shell, pages
    ├── js/                  # ES modules, no bundler (core/ and pages/)
    ├── images/              # Sprite, favicon, demo QR
    └── vendor/fonts/
docs/                        # Architecture, design system, integration notes
tests/                       # Smoke tests for page rendering
```

See [`docs/frontend-architecture.md`](docs/frontend-architecture.md),
[`docs/design-system.md`](docs/design-system.md), and
[`docs/integration-contract.md`](docs/integration-contract.md).

## Development workflow

Work happens on the personal branch `rachmad`, with Conventional Commits and a
pull request per coherent slice:

```bash
git checkout rachmad
git add <files>
git commit -m "feat(public): build landing page from design system"
git push -u origin rachmad
```

Keep commits scoped: scaffold, design system, page, docs. Avoid mixing template
rewrites with data-layer changes. The PR template includes a review checklist.

Current branch plan:

1. `rachmad` — foundation, design system, landing, style guide
2. Event catalog, event detail, and account screens
3. Participant dashboard, enrollment, tickets
4. Operator scanner flow
5. Admin panels and CV lab shell
6. Polish, accessibility audit, integration

## Design direction

Editorial and event-poster inspired: warm paper, near-black ink, one vermilion
accent, hairlines instead of shadows, and a serif display face. Typographic
event covers replace stock photography. See the live catalogue at
`/dev/styleguide`.

## Privacy note

Do not commit real facial images, biometric features, model artifacts, or
secrets. The final pipeline runs server-side; the browser only captures frames
and displays verdicts.

## Credits

- Methodology reference: *Attendance System with Face Recognition Using K-Nearest
  Neighbor, Particle Swarm Optimization, and Histogram of Oriented Gradients*,
  JESSI Vol. 7 No. 4, 2026.
- Instrument Sans and Instrument Serif are licensed under the SIL Open Font
  License; license files are in `app/static/vendor/fonts/`.