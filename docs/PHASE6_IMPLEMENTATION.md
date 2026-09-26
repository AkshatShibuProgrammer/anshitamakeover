# Phase 6 Implementation — Beauty Plan Booking Enquiry

## Completed

Added a server-backed booking enquiry foundation for the existing cart/Beauty Plan.

### New model

```text
BookingEnquiry
```

Stores:

- Name.
- Phone.
- Email.
- Event date.
- City.
- Notes.
- Cart item snapshot.
- Estimated total.
- Enquiry status.
- Created timestamp.

### New API

```text
POST /api/booking/
```

Behavior:

- Requires name and phone.
- Accepts event details and cart snapshot.
- Stores the estimated total as a server record.
- Returns a booking enquiry ID.
- Returns 400 for invalid details.
- Returns 405 for non-POST requests.

### Migration

```text
django/core/migrations/0014_bookingenquiry.py
```

## Validation

```text
unit PASS — 228 tests
api PASS — 28 tests
smoke PASS
perf PASS — p95 213 ms, 0 errors
coverage 65%
e2e SKIP — Chromium unavailable locally
bdd SKIP — Java/Maven unavailable locally
```

## Remaining Phase 6 work

- Connect the existing cart submit button to `/api/booking/`.
- Add booking form validation and success state.
- Add admin enquiry list/status management.
- Generate WhatsApp summary after enquiry creation.
- Add dedicated booking tests.
