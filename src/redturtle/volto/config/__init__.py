import os

MAX_LIMIT = str(
    os.environ.get("REDTURTLE_VOLTO_MAX_LIMIT_SEARCH", None) or 500
)
