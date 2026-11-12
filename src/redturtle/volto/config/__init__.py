import os

MAX_LIMIT = int(os.environ.get("REDTURTLE_VOLTO_MAX_LIMIT_SEARCH") or 500)

DEFAULT_MAX_NAVIGATION_DEPTH = 3


def _positive_int_from_env(name):
    """Return the env var as an int > 0, or None if missing, empty, invalid or <= 0."""
    try:
        value = int(os.environ.get(name) or "")
    except ValueError:
        return None
    return value if value > 0 else None


MAX_NAVIGATION_DEPTH = _positive_int_from_env("REDTURTLE_VOLTO_MAX_NAVIGATION_DEPTH")

DEFAULT_MAX_NAVIGATION_ITEMS = 1000


def _int_from_env(name, default):
    """Return the env var as an int, or default if missing, empty or invalid."""
    try:
        return int(os.environ.get(name) or default)
    except ValueError:
        return default


# <= 0 means no cap
MAX_NAVIGATION_ITEMS = _int_from_env(
    "REDTURTLE_VOLTO_MAX_NAVIGATION_ITEMS", DEFAULT_MAX_NAVIGATION_ITEMS
)
