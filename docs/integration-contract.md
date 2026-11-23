# Integration contract

This document is the hand-off seam between the frontend and the backend team.
It records the data each page expects and the endpoints the interactive modules
will call. Keep it updated when a page changes its context.

## Rules

1. Templates never import fixtures, ORM models, or services.
2. Page controllers return plain objects whose attribute names match the backend
   model fields. Add derived presentation fields as properties on the object.
3. The demo repository and the live repository must expose the same methods.
4. Mock endpoints live under `app/mock/` and are registered only when
   `DEMO_MODE=true`. Removing the registration is the only change required to
   switch to the real API.
5. A failed face verification must never mark a ticket as used.

## Demo identity

There is no session layer yet. Participant routes render the single fixture user
returned by `repository.user_for_role("participant")` and are gated on
`DEMO_MODE`, returning 404 otherwise. The topbar role switcher is a demo control,
not an authorization boundary.

When auth lands:

- Replace `_guard_demo()` in `app/web/routes/participant.py` with a session
  dependency that resolves the signed-in user.
- Drop `user_for_role()` from page controllers; pass the session user instead.
- Set `DEMO_ROLES[*].available` from the session role and point `href` at the
  real landing route for that role.
- Keep the demo strip only while `DEMO_MODE=true`; it is rendered from
  `base_app.html`.

## Page context

| Template | Context keys | Notes |
| --- | --- | --- |
| `public/landing.html` | `events`, `hero_event` | `events` is a curated list, not the next three by date |
| `public/events.html` | `events`, `categories`, `query`, `category`, `total_events` | Filtering is server-side; `total_events` is the unfiltered count |
| `public/event_details.html` | `event`, `related` | No ticket state yet; the CTA links to sign-in |
| `public/login.html` | `next`, `form_email`, `notice` | `notice` is set after a demo POST |
| `public/register.html` | `next`, `form_name`, `form_email`, `notice` | Same demo POST behaviour |
| `participant/dashboard.html` | `user`, `face_profile`, `sample_count`, `target_samples`, `tickets`, `active_ticket_count`, `registrations`, `next_ticket` | `next_ticket` is the soonest active pass for an event that has not started |
| `participant/enrollment.html` | `user`, `face_profile`, `sample_count`, `poses`, `target_samples` | Poses are labels and instructions, not coordinates |
| `participant/tickets.html` | `user`, `tickets` | Active passes first, then the most recent events |
| `participant/ticket_detail.html` | `user`, `ticket` | QR is fetched from `participant_ticket_qr`, never embedded as a data URI |
| `operator/dashboard.html` | `events`, `recent_logs` | Only assigned events |
| `operator/scanner.html` | `event`, `session` | Session is short-lived and ticket-scoped |
| `admin/dashboard.html` | `metrics`, `logs`, `model_info`, `gallery_count` | No invented analytics |
| `admin/events.html` | `events` | |
| `cv_lab/index.html` | `pipeline_report` | Only after the backend returns real values |
| `cv_lab/experiments.html` | `report` | Rendered from `experiment_report.json` |

## Model fields

### Event

Backend: `id`, `title`, `description`, `location`, `start_at`, `end_at`,
`registration_open_at`, `registration_close_at`, `checkin_open_at`,
`checkin_close_at`, `capacity`, `status`, `created_at`.

Presentation-only fields currently on `DemoEvent`: `category`, `city`, `organizer`,
`accent`, `registered_count`, `date_short`, `date_long`, `time_short`, `initial`,
`capacity_pct`, `spots_left`, `is_sold_out`, `is_registration_open`, `schedule`,
`url`.

`registered_count` is a count of confirmed registrations; `accent`, `city`, and
`organizer` must be added to the event record or derived from a small
presentation map. Do not hard-code them in the template.

### Ticket

`id`, `event_id`, `registration_id`, `user_id`, `token_hash`, `status`,
`issued_at`, `used_at`. `status` is one of `ACTIVE`, `USED`, `CANCELLED`.

The demo fixture carries `code` (the raw token) so the pass sheet can show a
manual entry token and generate a QR. A real backend should expose the raw token
only at issuance, serve the QR from a ticket-scoped endpoint, and keep
`token_hash` as the stored value. `seat` is optional; when absent, hide the seat
row instead of inventing a value.

Presentation fields on the demo views: `DemoTicketView.short_code`, `is_active`,
`is_used`; `DemoRegistrationView.ticket_status` (falls back to `PENDING`).

### Face profile and registration

Backend `FaceProfile`: `id`, `user_id`, `enrollment_status`
(`PENDING`, `IN_PROGRESS`, `COMPLETED`, `FAILED`), `sample_count`, `updated_at`.
`FaceSample` rows stay server-side; never send descriptors or images to the
browser.

Backend `Registration`: `id`, `user_id`, `event_id`, `status`, `created_at`,
`ticket_id`. The dashboard joins it with the event and the ticket.

### User

`id`, `name`, `email`, `role` (`participant`, `operator`, `admin`), plus
`face_profile` and enrollment state on participant pages.

### Check-in log

`ticket_id`, `operator_id`, `result` (`GRANTED`, `DENIED`), `failure_reason`,
`model_version_id`, `created_at`. The admin table joins ticket → event and user.

## Interactive endpoints

| Module | Endpoint | Payload | Response |
| --- | --- | --- | --- |
| Auth | `POST /auth/login` | `email`, `password` form | Session cookie + redirect |
| Auth | `POST /auth/register` | `name`, `email`, `password` form | Session cookie + redirect |
| Auth | `GET /auth/logout` | — | Clears cookie |
| Participant | `GET /participant/tickets/{id}/qr.png` | — | PNG QR for the ticket token; `Cache-Control: no-store` |
| Enrollment | `POST /api/enrollment/sample` | `image_base64`, `pose_label` | Quality result, accepted flag |
| Enrollment | `POST /api/enrollment/complete` | `consent` | Success or rejection reason |
| Check-in | `POST /api/checkin/validate-qr` | `qr_token` | Ticket summary + session id + expiry |
| Check-in | `POST /api/checkin/verify-face` | `session_id`, `image_base64` | Verdict, distance, threshold, reason |
| CV lab | `POST /api/cv-lab/inspect` | `image_base64` | Visualization maps + ML decision |
| Admin | `POST /admin/events/new` | event form | Redirect or validation error |

All state-changing browser requests must carry the session cookie and, in
production, a CSRF token. The frontend will read the CSRF token from a meta tag
or a cookie set by the backend, not from a hard-coded value.

## JavaScript callers

| File | Depends on | Notes |
| --- | --- | --- |
| `js/core/nav.js` | DOM only | No backend |
| `js/core/app-shell.js` | DOM only | Mobile sidebar and role switcher |
| `js/pages/enrollment.js` | `navigator.mediaDevices` | Local capture only; no fetch, no descriptor. Replace the save handler when `/api/enrollment/*` exists |
| `js/core/api.js` (next) | `fetch`, session cookie | Central JSON/error handling |
| `js/modules/camera.js` (next) | `navigator.mediaDevices` | Releases tracks on unmount |
| `js/modules/scanner.js` (next) | `/api/checkin/*` | Two-stage wizard, countdown |
| `js/modules/cv-lab.js` (next) | `/api/cv-lab/inspect` | Never claims results without a response |

## Demo router

The participant workspace ships without a mock API: enrollment keeps frames in
the browser and its save button stops at a notice. During the scanner PR,
`app/mock/api.py` will expose the interactive endpoints with deterministic demo
responses. It must:

- Return a visible `demo: true` flag.
- Never be registered when `DEMO_MODE=false`.
- Not pretend to run the real HOG/K-NN pipeline.

## Error shape

Use a consistent JSON body for API failures:

```json
{
  "detail": "Face distance above threshold",
  "code": "FACE_MISMATCH",
  "attempt_id": "chk-…"
}
```

The UI shows `detail` to the operator, logs `code` for the audit trail, and
never exposes raw distances to participants.