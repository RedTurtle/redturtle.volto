from plone import api
from plone.api.exc import InvalidParameterError
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.restapi.services.navigation.get import Navigation as BaseNavigation
from plone.restapi.testing import RelativeSession
from redturtle.volto import config
from redturtle.volto.restapi.services.navigation.limits import (
    apply_navigation_items_cap,
)
from redturtle.volto.restapi.services.navigation.limits import get_max_navigation_depth
from redturtle.volto.restapi.services.navigation.limits import prune_navigation_tree
from redturtle.volto.restapi.services.navigation.navigation import Navigation
from redturtle.volto.testing import REDTURTLE_VOLTO_API_FUNCTIONAL_TESTING
from unittest import mock
from zope.annotation.interfaces import IAnnotations

import importlib
import os
import transaction
import unittest

LIMITS_LOGGER = "redturtle.volto.restapi.services.navigation.limits"


def tree_depth(items):
    """Count the nested levels of a navigation tree (items -> items -> ...)."""
    if not items:
        return 0
    return 1 + max(tree_depth(item.get("items", [])) for item in items)


def count_items(items):
    """Count all the nodes of a navigation tree."""
    return sum(1 + count_items(item.get("items") or []) for item in items)


def build_tree(*widths, keep_empty_key=True):
    """Build a tree where every node of level n has widths[n] children."""
    if not widths:
        return []
    items = []
    for i in range(widths[0]):
        node = {"@id": f"node-{len(widths)}-{i}"}
        children = build_tree(*widths[1:], keep_empty_key=keep_empty_key)
        if children or keep_empty_key:
            node["items"] = children
        items.append(node)
    return items


class TestNavigationLimits(unittest.TestCase):
    layer = REDTURTLE_VOLTO_API_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

        container = self.portal
        for i in range(1, 6):
            container = api.content.create(
                container=container, type="Folder", id=f"l{i}", title=f"L{i}"
            )
        transaction.commit()

    def tearDown(self):
        self.api_session.close()

    def get_navigation(self, depth):
        response = self.api_session.get(f"/@navigation?expand.navigation.depth={depth}")
        self.assertEqual(response.status_code, 200)
        return response.json()["items"]

    def test_tree_depth_matches_requested_depth(self):
        for depth in (1, 2, 3):
            self.assertEqual(tree_depth(self.get_navigation(depth)), depth)

    def test_navigation_depth_too_high_is_clamped(self):
        with self.assertLogs(LIMITS_LOGGER, level="WARNING") as logs:
            items = self.get_navigation(70)
        self.assertEqual(tree_depth(items), 3)
        self.assertEqual(len(logs.records), 1)
        self.assertIn("=70", logs.output[0])
        self.assertIn("clamped to 3", logs.output[0])

    def test_navigation_expander_depth_too_high_is_clamped(self):
        response = self.api_session.get(
            "/?expand=navigation&expand.navigation.depth=70"
        )
        self.assertEqual(response.status_code, 200)
        items = response.json()["@components"]["navigation"]["items"]
        self.assertEqual(tree_depth(items), 3)

    def test_navigation_negative_depth_is_clamped(self):
        self.assertEqual(tree_depth(self.get_navigation(-1)), 3)

    def test_navigation_depth_within_limit_is_unchanged(self):
        self.assertEqual(tree_depth(self.get_navigation(2)), 2)

    def test_navigation_depth_within_limit_same_output_as_plone_restapi(self):
        request = self.layer["request"]
        request.form["expand.navigation.depth"] = "2"
        annotations = IAnnotations(request)
        # both classes are named "Navigation": don't share the plone.memoize cache
        annotations.pop("plone.memoize", None)
        expected = BaseNavigation(self.portal, request)(expand=True)
        annotations.pop("plone.memoize", None)
        result = Navigation(self.portal, request)(expand=True)
        self.assertEqual(result, expected)
        self.assertEqual(request.form["expand.navigation.depth"], "2")

    def test_navigation_depth_uses_registry(self):
        api.portal.set_registry_record("plone.navigation_depth", 4)
        transaction.commit()
        self.assertEqual(tree_depth(self.get_navigation(70)), 4)

    def test_navigation_depth_env_var_wins_over_registry(self):
        api.portal.set_registry_record("plone.navigation_depth", 4)
        transaction.commit()
        with mock.patch("redturtle.volto.config.MAX_NAVIGATION_DEPTH", 2):
            self.assertEqual(tree_depth(self.get_navigation(70)), 2)

    def test_navigation_depth_not_an_integer(self):
        response = self.api_session.get("/@navigation?expand.navigation.depth=foo")
        self.assertEqual(response.status_code, 400)

    def test_context_navigation_depth_too_high_is_clamped(self):
        response = self.api_session.get(
            "/l1/@context-navigation?expand.navigation.depth=70"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(tree_depth(response.json()["items"]), 3)

    def test_context_navigation_depth_not_an_integer(self):
        response = self.api_session.get(
            "/l1/@context-navigation?expand.navigation.depth=foo"
        )
        self.assertEqual(response.status_code, 400)


class TestGetMaxNavigationDepth(unittest.TestCase):
    def get_max(self, registry_value=None, side_effect=None):
        with mock.patch("redturtle.volto.config.MAX_NAVIGATION_DEPTH", None):
            with mock.patch(
                "plone.api.portal.get_registry_record",
                return_value=registry_value,
                side_effect=side_effect,
            ):
                return get_max_navigation_depth()

    def test_env_var_wins(self):
        with mock.patch("redturtle.volto.config.MAX_NAVIGATION_DEPTH", 7):
            with mock.patch(
                "plone.api.portal.get_registry_record", return_value=4
            ) as registry:
                self.assertEqual(get_max_navigation_depth(), 7)
        registry.assert_not_called()

    def test_registry_value(self):
        self.assertEqual(self.get_max(registry_value=4), 4)

    def test_registry_missing(self):
        self.assertEqual(self.get_max(registry_value=None), 3)
        self.assertEqual(self.get_max(side_effect=InvalidParameterError("x")), 3)
        self.assertEqual(self.get_max(side_effect=KeyError("x")), 3)

    def test_registry_invalid(self):
        for value in (0, -1, "abc", "4", True):
            self.assertEqual(self.get_max(registry_value=value), 3)


class TestConfigFromEnv(unittest.TestCase):
    ENV = "REDTURTLE_VOLTO_MAX_NAVIGATION_DEPTH"

    def tearDown(self):
        importlib.reload(config)

    def reload_with(self, value):
        with mock.patch.dict(os.environ, {self.ENV: value}):
            importlib.reload(config)
        return config.MAX_NAVIGATION_DEPTH

    def test_invalid_values(self):
        for value in ("abc", "0", "", "-2", "1.5"):
            self.assertIsNone(self.reload_with(value))

    def test_valid_value(self):
        self.assertEqual(self.reload_with("5"), 5)


class TestConfigItemsFromEnv(unittest.TestCase):
    ENV = "REDTURTLE_VOLTO_MAX_NAVIGATION_ITEMS"

    def tearDown(self):
        importlib.reload(config)

    def reload_with(self, value):
        with mock.patch.dict(os.environ, {self.ENV: value}):
            importlib.reload(config)
        return config.MAX_NAVIGATION_ITEMS

    def test_missing(self):
        with mock.patch.dict(os.environ, clear=False):
            os.environ.pop(self.ENV, None)
            importlib.reload(config)
        self.assertEqual(config.MAX_NAVIGATION_ITEMS, 1000)

    def test_invalid_values(self):
        for value in ("abc", "", "1.5"):
            self.assertEqual(self.reload_with(value), 1000)

    def test_valid_values(self):
        self.assertEqual(self.reload_with("50"), 50)
        self.assertEqual(self.reload_with("0"), 0)
        self.assertEqual(self.reload_with("-1"), -1)


class TestPruneNavigationTree(unittest.TestCase):
    def test_under_the_cap_is_unchanged(self):
        items = build_tree(2, 3, 2)
        expected = build_tree(2, 3, 2)
        self.assertEqual(prune_navigation_tree(items, 20), (20, 20))
        self.assertEqual(items, expected)
        self.assertEqual(prune_navigation_tree(items, 1000), (20, 20))
        self.assertEqual(items, expected)

    def test_cut_level_3(self):
        items = build_tree(2, 3, 2)
        self.assertEqual(prune_navigation_tree(items, 10), (20, 8))
        self.assertEqual(len(items), 2)
        self.assertEqual(count_items(items), 8)
        for node in items:
            self.assertEqual(len(node["items"]), 3)
            for child in node["items"]:
                self.assertEqual(child["items"], [])

    def test_cap_smaller_than_level_1(self):
        items = build_tree(5, 2)
        self.assertEqual(prune_navigation_tree(items, 3), (15, 5))
        self.assertEqual(len(items), 5)
        for node in items:
            self.assertEqual(node["items"], [])

    def test_keep_empty_key_false(self):
        items = build_tree(2, 3, 2, keep_empty_key=False)
        self.assertEqual(
            prune_navigation_tree(items, 10, keep_empty_key=False), (20, 8)
        )
        for node in items:
            self.assertEqual(len(node["items"]), 3)
            for child in node["items"]:
                self.assertNotIn("items", child)

    def test_uneven_tree_never_has_holes(self):
        # level 1: 3 nodes, level 2: 1 + 0 + 4 nodes, level 3: 6 nodes
        items = [
            {"@id": "a", "items": build_tree(1, 6)},
            {"@id": "b", "items": []},
            {"@id": "c", "items": build_tree(4)},
        ]
        self.assertEqual(prune_navigation_tree(items, 10), (14, 8))
        self.assertEqual(len(items[0]["items"]), 1)
        self.assertEqual(items[0]["items"][0]["items"], [])
        self.assertEqual(len(items[2]["items"]), 4)

    def test_max_items_zero_never_cuts(self):
        items = build_tree(2, 3, 2)
        self.assertEqual(prune_navigation_tree(items, 0), (20, 20))
        self.assertEqual(count_items(items), 20)


class TestApplyNavigationItemsCap(unittest.TestCase):
    def setUp(self):
        self.request = {"ACTUAL_URL": "http://nohost/plone/@navigation"}

    def test_cap_off(self):
        for value in (0, -1):
            items = build_tree(2, 3, 2)
            with mock.patch("redturtle.volto.config.MAX_NAVIGATION_ITEMS", value):
                with self.assertNoLogs(LIMITS_LOGGER, level="WARNING"):
                    apply_navigation_items_cap(items, self.request)
            self.assertEqual(count_items(items), 20)

    def test_under_the_cap_no_warning(self):
        items = build_tree(2, 3, 2)
        with mock.patch("redturtle.volto.config.MAX_NAVIGATION_ITEMS", 20):
            with self.assertNoLogs(LIMITS_LOGGER, level="WARNING"):
                apply_navigation_items_cap(items, self.request)
        self.assertEqual(count_items(items), 20)

    def test_pruned_logs_one_warning(self):
        items = build_tree(2, 3, 2)
        with mock.patch("redturtle.volto.config.MAX_NAVIGATION_ITEMS", 10):
            with self.assertLogs(LIMITS_LOGGER, level="WARNING") as logs:
                apply_navigation_items_cap(items, self.request)
        self.assertEqual(count_items(items), 8)
        self.assertEqual(len(logs.records), 1)
        self.assertIn("pruned from 20 to 8 items (max 10)", logs.output[0])
        self.assertIn("http://nohost/plone/@navigation", logs.output[0])


class TestNavigationItemsCap(unittest.TestCase):
    layer = REDTURTLE_VOLTO_API_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

        # 2 + 6 + 12 = 20 folders
        for i in range(2):
            folder = api.content.create(
                container=self.portal, type="Folder", id=f"f{i}", title=f"F{i}"
            )
            for j in range(3):
                sub = api.content.create(
                    container=folder, type="Folder", id=f"f{i}{j}", title=f"F{i}{j}"
                )
                for k in range(2):
                    api.content.create(
                        container=sub,
                        type="Folder",
                        id=f"f{i}{j}{k}",
                        title=f"F{i}{j}{k}",
                    )
        api.portal.set_registry_record("plone.navigation_depth", 3)
        transaction.commit()

    def tearDown(self):
        self.api_session.close()

    def get_navigation(self):
        response = self.api_session.get("/@navigation?expand.navigation.depth=3")
        self.assertEqual(response.status_code, 200)
        return response.json()["items"]

    def get_expander_navigation(self):
        response = self.api_session.get("/?expand=navigation&expand.navigation.depth=3")
        self.assertEqual(response.status_code, 200)
        return response.json()["@components"]["navigation"]["items"]

    def assert_pruned_to_level_2(self, items):
        # level 1 also contains the tabs that are not folders (e.g. Home)
        folders = [item for item in items if item["items"]]
        self.assertEqual(len(folders), 2)
        self.assertEqual(count_items(items), len(items) + 6)
        self.assertEqual(tree_depth(items), 2)
        for folder in folders:
            self.assertEqual(len(folder["items"]), 3)
            for child in folder["items"]:
                self.assertEqual(child["items"], [])

    def test_navigation_pruned(self):
        with mock.patch("redturtle.volto.config.MAX_NAVIGATION_ITEMS", 10):
            with self.assertLogs(LIMITS_LOGGER, level="WARNING") as logs:
                items = self.get_navigation()
        self.assert_pruned_to_level_2(items)
        self.assertEqual(len(logs.records), 1)
        self.assertIn("tree pruned from", logs.output[0])

    def test_navigation_expander_pruned(self):
        with mock.patch("redturtle.volto.config.MAX_NAVIGATION_ITEMS", 10):
            items = self.get_expander_navigation()
        self.assert_pruned_to_level_2(items)

    def test_navigation_cap_off(self):
        with mock.patch("redturtle.volto.config.MAX_NAVIGATION_ITEMS", 0):
            items = self.get_navigation()
        self.assertEqual(tree_depth(items), 3)
        self.assertEqual(count_items(items), len(items) + 18)

    def test_navigation_under_the_cap_same_output_as_plone_restapi(self):
        request = self.layer["request"]
        request.form["expand.navigation.depth"] = "3"
        annotations = IAnnotations(request)
        # both classes are named "Navigation": don't share the plone.memoize cache
        annotations.pop("plone.memoize", None)
        expected = BaseNavigation(self.portal, request)(expand=True)
        annotations.pop("plone.memoize", None)
        result = Navigation(self.portal, request)(expand=True)
        self.assertEqual(result, expected)
        self.assertEqual(count_items(result["navigation"]["items"]), 21)

    def test_context_navigation_pruned(self):
        with mock.patch("redturtle.volto.config.MAX_NAVIGATION_ITEMS", 1):
            with self.assertLogs(LIMITS_LOGGER, level="WARNING") as logs:
                response = self.api_session.get(
                    "/f0/@context-navigation?expand.navigation.depth=3"
                )
        self.assertEqual(response.status_code, 200)
        items = response.json()["items"]
        self.assertEqual(len(items), 3)
        for item in items:
            self.assertNotIn("items", item)
        self.assertEqual(len(logs.records), 1)

    def test_context_navigation_under_the_cap(self):
        with mock.patch("redturtle.volto.config.MAX_NAVIGATION_ITEMS", 1000):
            response = self.api_session.get(
                "/f0/@context-navigation?expand.navigation.depth=3"
            )
        self.assertEqual(response.status_code, 200)
        items = response.json()["items"]
        self.assertEqual(count_items(items), 9)
        for item in items:
            self.assertEqual(len(item["items"]), 2)
            for child in item["items"]:
                self.assertNotIn("items", child)
