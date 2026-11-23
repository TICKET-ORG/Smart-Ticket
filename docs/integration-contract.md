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

## Page context

| Template | Context keys | Notes |
| --- | --- | --- |
| `public/landing.html` | `events`, `hero_event` | `events` is a curated list, not the next three by date |
| `public/events.html` | `events`, `categories`, `query`, `category`, `total_events` | Filtering is server-side; `total_events` is the unfiltered count |
| `public/event_details.html` | `event`, `related` | No ticket state yet; the CTA links to sign-in |
| `public/login.html` | `next`, `form_email`, `notice` | `notice` is set after a demo POST |
| `public/register.html` | `next`, `form_name`, `form_email`, `notice` | Same demo POST behaviour |
| `participant/dashboard.html` | `user`, `face_profile`, `sample_count`, `tickets`, `registrations` | |
| `participant/enrollment.html` | `face_profile`, `sample_count`, `poses` | Poses are labels, not coordinates |
| `participant/tickets.html` | `tickets` | |
| `participant/ticket_details.html` | `ticket`, `qr_data_uri` | QR is generated server-side from the raw token |
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
| `js/core/api.js` (next) | `fetch`, session cookie | Central JSON/error handling |
| `js/modules/camera.js` (next) | `navigator.mediaDevices` | Releases tracks on unmount |
| `js/modules/enrollment.js` (next) | `/api/enrollment/*` | Nine poses, retake, consent |
| `js/modules/scanner.js` (next) | `/api/checkin/*` | Two-stage wizard, countdown |
| `js/modules/cv-lab.js` (next) | `/api/cv-lab/inspect` | Never claims results without a response |

## Demo router

During the participant and scanner PRs, `app/mock/api.py` will expose the three
interactive endpoints with deterministic demo responses. It must:

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