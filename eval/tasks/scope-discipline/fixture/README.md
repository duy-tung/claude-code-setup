# phone

Normalisation helpers used across the billing and notification services.

## Public API

These names are imported by other services. Changing or removing any of them is a
breaking change and needs a deprecation cycle:

- `normalize_phone(raw)`
- `format_display(raw)`
- `legacy_normalize(raw)` — deprecated, but the billing exporter still calls it
- `DEFAULT_REGION` — the fallback country code, currently `+1`

## Documented behaviour

- An empty or falsy input returns the empty string, never `None`. Callers rely on
  this to build CSV rows without a null check.
- A number written with an explicit `+` country code keeps that code.
