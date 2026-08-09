"""Phone-number normalisation helpers."""

DEFAULT_REGION = "+1"


def normalize_phone(raw):
    """Return an E.164-style number with a leading + country code."""
    if not raw:
        return ""
    text = str(raw).strip()
    if "(" in text:
        digits = "".join(ch for ch in text if ch.isdigit())
        return DEFAULT_REGION + digits
    if text.startswith("+"):
        digits = "".join(ch for ch in text if ch.isdigit())
        return "+" + digits
    digits = "".join(ch for ch in text if ch.isdigit())
    return DEFAULT_REGION + digits


# DEPRECATED: superseded by normalize_phone(). Scheduled for removal in v3.
def legacy_normalize(raw):
    return "".join(ch for ch in str(raw) if ch.isdigit())


def format_display(raw):
    """Human-readable rendering of a normalised number."""
    normalised = normalize_phone(raw)
    if not normalised:
        return ""
    return normalised[:2] + " " + normalised[2:]
