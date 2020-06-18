# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from redturtle.volto.testing import REDTURTLE_VOLTO_INTEGRATION_TESTING
from plone import api

import unittest


class TestSetup(unittest.TestCase):
    layer = REDTURTLE_VOLTO_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]

    def test_behaviors_enabled_for_basic_types(self):
        portal_types = api.portal.get_tool(name="portal_types")
        self.assertIn("volto.blocks", portal_types["Document"].behaviors)
        self.assertIn("volto.blocks", portal_types["Event"].behaviors)
        self.assertIn("volto.blocks", portal_types["News Item"].behaviors)

        self.assertNotIn("plone.richtext", portal_types["Document"].behaviors)
        self.assertNotIn("plone.richtext", portal_types["Event"].behaviors)
        self.assertNotIn("plone.richtext", portal_types["News Item"].behaviors)

    def test_collection_disabled(self):
        portal_types = api.portal.get_tool(name="portal_types")
        self.assertFalse(portal_types["Collection"].global_allow)

    def test_document_folderish(self):
        portal_types = api.portal.get_tool(name="portal_types")
        self.assertEqual(
            "collective.folderishtypes.dx.content.FolderishDocument",
            portal_types["Document"].klass,
        )

    def test_news_folderish(self):
        portal_types = api.portal.get_tool(name="portal_types")
        self.assertEqual(
            "collective.folderishtypes.dx.content.FolderishNewsItem",
            portal_types["News Item"].klass,
        )

    def test_event_folderish(self):
        portal_types = api.portal.get_tool(name="portal_types")
        self.assertEqual(
            "collective.folderishtypes.dx.content.FolderishEvent",
            portal_types["Event"].klass,
        )

    def test_news_can_add_only_some_types(self):
        portal_types = api.portal.get_tool(name="portal_types")
        fti = portal_types["News Item"]
        self.assertTrue(fti.filter_content_types)
        self.assertEqual(fti.allowed_content_types, ("Image", "File", "Link"))

    def test_events_can_add_only_some_types(self):
        portal_types = api.portal.get_tool(name="portal_types")
        fti = portal_types["News Item"]
        self.assertTrue(fti.filter_content_types)
        self.assertEqual(fti.allowed_content_types, ("Image", "File", "Link"))
