from plone import api
from plone.api.exc import InvalidParameterError
from redturtle.volto import config
from zExceptions import BadRequest

import logging


logger = logging.getLogger(__name__)

DEPTH_PARAM = "expand.navigation.depth"


def parse_int(data, prop, default):
    """
    Copy of plone.restapi.deserializer.parse_int, that is not available in
    plone.restapi 9.6.0 (our minimum version).

    Raises BadRequest if the value is not an int.
    """
    try:
        return int(data.get(prop, default))
    except (ValueError, TypeError):
        raise BadRequest(f"Invalid {prop}: Not an integer")


def get_max_navigation_depth():
    """env var > registry plone.navigation_depth > DEFAULT_MAX_NAVIGATION_DEPTH"""
    if config.MAX_NAVIGATION_DEPTH is not None:
        return config.MAX_NAVIGATION_DEPTH
    try:
        value = api.portal.get_registry_record("plone.navigation_depth", default=None)
    except (InvalidParameterError, KeyError):
        value = None
    if isinstance(value, int) and not isinstance(value, bool) and value >= 1:
        return value
    return config.DEFAULT_MAX_NAVIGATION_DEPTH


def clamp_navigation_depth(request, default=1):
    """Read DEPTH_PARAM from request.form with parse_int (BadRequest if not an int),
    lower it to the maximum if it is > max or < 0, write the clamped value back into
    request.form when it changes, and log a warning. Return the depth to use."""
    if not request.form.get(DEPTH_PARAM, False):
        # missing or empty: same fallback as plone.restapi
        return default
    depth = parse_int(request.form, DEPTH_PARAM, default)
    max_depth = get_max_navigation_depth()
    if 0 <= depth <= max_depth:
        return depth
    logger.warning(
        "[navigation] %s=%s out of range, clamped to %s (%s)",
        DEPTH_PARAM,
        depth,
        max_depth,
        request.get("ACTUAL_URL"),
    )
    request.form[DEPTH_PARAM] = max_depth
    return max_depth


def count_navigation_items(items):
    """Count all the nodes of a navigation tree."""
    return sum(1 + count_navigation_items(item.get("items") or []) for item in items)


def prune_navigation_tree(items, max_items, keep_empty_key=True):
    """Cut `items` (a list of nodes, each with optional "items" children) to whole
    levels, breadth-first, so that the total number of nodes is <= max_items.
    The first level is always kept. Changes `items` in place.
    keep_empty_key=True  -> cut nodes get "items": []   (@navigation shape)
    keep_empty_key=False -> cut nodes lose the "items" key (@context-navigation shape)
    Returns a tuple (total_before, total_after); equal if nothing was cut."""
    level = items
    kept = len(level)
    while level:
        children = [child for node in level for child in (node.get("items") or [])]
        if not children:
            break
        if max_items > 0 and kept + len(children) > max_items:
            total_before = kept + count_navigation_items(children)
            for node in level:
                if keep_empty_key:
                    node["items"] = []
                else:
                    node.pop("items", None)
            return total_before, kept
        kept += len(children)
        level = children
    return kept, kept


def apply_navigation_items_cap(items, request, keep_empty_key=True):
    """Prune the navigation tree to config.MAX_NAVIGATION_ITEMS (no cap if <= 0)
    and log a warning if something was cut."""
    max_items = config.MAX_NAVIGATION_ITEMS
    if max_items <= 0:
        return
    total_before, total_after = prune_navigation_tree(
        items, max_items, keep_empty_key=keep_empty_key
    )
    if total_before != total_after:
        logger.warning(
            "[navigation] tree pruned from %s to %s items (max %s) (%s)",
            total_before,
            total_after,
            max_items,
            request.get("ACTUAL_URL"),
        )
