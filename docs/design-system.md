# Design system

## Direction

SmartTicket should read like an event poster, not a SaaS dashboard. The system
is editorial: warm paper, ink typography, one signal accent, and structure built
from hairlines and whitespace. Photography is replaced with typographic covers
so the interface does not depend on stock imagery.

Avoid: blue-purple gradients, glassmorphism, giant rounded cards everywhere,
emoji as icons, floating blobs, shadow-heavy panels, generic three-card feature
grids, and animation for decoration.

## Color

| Token | Value | Use |
| --- | --- | --- |
| `--paper` | `#f6f3ec` | Page background |
| `--paper-raised` | `#fbf9f3` | Cards, panels, inputs |
| `--ink` | `#131210` | Primary text, primary buttons, dark bands |
| `--ink-2` | `#2d2a25` | Body copy |
| `--muted` | `#6c665b` | Secondary copy, labels |
| `--line` | `#dcd5c7` | Default borders |
| `--accent` | `#d8412a` | Signal: links on hover, marks, focus |
| `--green` | `#1f5a45` | Success, granted |
| `--amber` | `#8a5a12` | Warning, pending |
| `--blue` | `#34486b` | Informational |
| `--danger` | `#a92b1d` | Denied, destructive |

Use accent sparingly. A screen should have one accent action or marker, not
five. Status colors are always paired with a text label.

## Typography

- **Display / editorial:** Instrument Serif 400. Use for page titles, section
  titles, event names, ticket names, large numbers.
- **UI / body:** Instrument Sans 400–650. Use for paragraphs, labels, buttons,
  tables.
- **Code / numerals:** system mono. Use for tokens, timestamps, metric values.

Rules:

- Display text is tight: `line-height: 0.96–1.05`, slightly negative tracking.
- Body copy stays between 46 and 62 characters per line.
- Uppercase only for eyebrows, labels, and badges; always with letter spacing.
- Do not use more than two weights on one screen.

## Spacing and shape

- 4px base scale, with section rhythm from `--space-*`.
- Page container: `min(100% - 2.5rem, 1180px)`.
- Radii: 2px for tags, 4px for controls, 8–14px for cards, full for pills.
- Shadows: only the ticket stub. Everything else is a border.

## Components

### Buttons

One primary per surface. Primary is ink, accent is reserved for a deliberate
secondary signal, outline for neutral actions, ghost for low-emphasis controls.
Minimum target height is 2.6rem; 2.1rem for small controls.

### Forms

Labels above inputs. Hints below. Errors attached to the field with
`aria-invalid="true"`. No floating labels, no placeholder-only inputs.

### Event card

A typographic cover in the event accent, with category, status, title, date, and
city. The body carries venue, capacity, and one link. The cover is data-driven:
`style="--cover: {{ event.accent }}"`.

### Ticket stub

The stub is a two-column dark card. Perforation is created with two paper-colored
circles, not an image. The QR block is a paper square so it scans in low light.
The stub never shows a fake "verified" state.

### Status

Badge variants: neutral, success (`GRANTED`), danger (`DENIED`), warning,
info, accent. Status is text first. The dot is decorative and hidden on
`badge--plain`.

### Scanner

Dark frame, corner brackets, one instruction line. The result screen is
full-bleed, large type, no confetti. Use `aria-live="polite"` for the verdict.

The implemented gate screen pairs a paper "read the pass" panel with an ink
"verify the holder" panel, so the two stages read as one sequence instead of a
stack of cards. A stepper above tracks pass → face → verdict. The camera stage is
ink with an accent-outlined frame; the pass card stays on paper because it is
data, not hardware. Nothing on this screen may display a match until the backend
returns one.

### Operator dashboard

Assigned venues are one hairline list; each row carries a serif date, the venue,
its gate window, and a single scan link. Scan history keeps the shared table
style and is labelled as sample data underneath. Metrics stay in one bordered
row so gate totals do not read like a sales dashboard.

### Admin dashboard

The programme list is the same hairline row pattern as the operator venue list,
extended with a capacity bar per row: date, event, then how full it is. The
right rail is one card of record counts, not a chart — there is no real
analytics source yet, so nothing here is allowed to look like a trend.

The registration roster uses the shared table plus two chip rows: venue, then
status. Chips in a second row stay visually subordinate because the venue is the
coarser filter. The event form is a plain two/three-column field grid inside one
hairline panel; its submit button is styled like any other, and the demo notice
appears at the top of the form rather than in a modal.

### Catalog controls

Search is a single bordered field with an icon submit button; categories are
chips, not a dropdown. Active chip inverts to ink. Filtering happens on the
server through query params, so the state is shareable and survives a reload.

### Event detail

The event accent becomes a full-bleed cover band with an oversized serif title
and a hairline meta row. Below it, a two-column layout: reading column on the
left, sticky registration card on the right. The schedule is rendered from the
event's own timestamps — never invented.

### Account screens

Split layout: an ink panel carrying the promise ("Your face is the ticket."),
and a paper column with the form. Fields keep the standard label-above-input
pattern. Because there is no session layer yet, a submit re-renders the page
with a demo notice instead of pretending to sign anyone in.

### Application shell

Signed-in pages keep the paper palette but switch to a two-column frame: a
268px sidebar with the brand, role label, and nav items, and a main column with
a sticky topbar. A thin accent strip at the top of the main column carries the
demo notice; it is the only persistent accent on the screen.

Nav links use a full-width hover fill and an inset 2px accent bar for the
current page. The role switcher is a native `details` element: avatar, name,
role, and chevron, with a menu that lists every implemented demo role; roles
without pages would appear disabled. On small screens the sidebar becomes an overlay with a scrim;
the menu button is the only control in the topbar.

Page headers pair an eyebrow with a serif title, and sections are separated by
hairlines rather than nested cards. Metrics sit in one bordered row with
internal dividers, so a dashboard does not become a wall of boxes. Tables keep
the same hairline style; below 700px rows stack into labelled blocks so the
action link never scrolls off-screen.

### Empty states

State what happened, then the next action. An empty table gets a message, not a
header over nothing.

## Motion

- Duration 160ms, easing `cubic-bezier(0.22, 0.75, 0.25, 1)`.
- One entrance animation on the landing hero; everything else is interaction
  feedback.
- Respect `prefers-reduced-motion: reduce` globally.
- No parallax, scroll-jacking, or looping decorative animation beyond the
  category ticker (which pauses on hover and is hidden from reduced motion by
  the global rule).

## Accessibility

- Skip link on every page.
- Visible `:focus-visible` outline on all interactive elements.
- Landmarks: header, nav, main, footer.
- Contrast: body text and controls meet WCAG AA on paper.
- Mobile navigation uses `aria-expanded` and closes on Escape.
- Images that are decorative get empty alt text; the demo QR has a descriptive
  alt because it is part of a sample ticket.
- Tables use `scope="col"` and readable headers.

## Page composition

1. Page header: eyebrow, serif title, one-sentence lede.
2. Primary content: one dominant column or grid; no competing panels.
3. Supporting detail: rules, lists, data tables.
4. One closing action.

Public pages use the shared `page-head` band. The event detail replaces it with
a full-bleed accent cover, since the event itself is the page's subject.

The landing page is the reference implementation of this rhythm. The style guide
at `/dev/styleguide` is the living catalogue of tokens and components.