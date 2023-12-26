# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.restapi.testing import RelativeSession
from redturtle.volto.testing import REDTURTLE_VOLTO_API_FUNCTIONAL_TESTING
from redturtle.volto.testing import REDTURTLE_VOLTO_INTEGRATION_TESTING

import unittest


class TestContentTypes(unittest.TestCase):
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
            "plone.volto.content.FolderishDocument",
            portal_types["Document"].klass,
        )

    def test_news_folderish(self):
        portal_types = api.portal.get_tool(name="portal_types")
        self.assertEqual(
            "plone.volto.content.FolderishNewsItem",
            portal_types["News Item"].klass,
        )

    def test_event_folderish(self):
        portal_types = api.portal.get_tool(name="portal_types")
        self.assertEqual(
            "plone.volto.content.FolderishEvent",
            portal_types["Event"].klass,
        )

    def test_news_can_add_only_some_types(self):
        portal_types = api.portal.get_tool(name="portal_types")
        fti = portal_types["News Item"]
        self.assertTrue(fti.filter_content_types)
        self.assertEqual(
            fti.allowed_content_types, ("Document", "Image", "File", "Link")
        )

    def test_events_can_add_only_some_types(self):
        portal_types = api.portal.get_tool(name="portal_types")
        fti = portal_types["News Item"]
        self.assertTrue(fti.filter_content_types)
        self.assertEqual(
            fti.allowed_content_types, ("Document", "Image", "File", "Link")
        )


class TestContentTypesSchema(unittest.TestCase):
    layer = REDTURTLE_VOLTO_API_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

    def tearDown(self):
        self.api_session.close()

    def test_link_remoteUrl_return_proper_widget(self):
        response = self.api_session.get("/@types/Link")
        res = response.json()

        self.assertEqual(res["properties"]["remoteUrl"]["widget"], "url")

    def test_link_remoteUrl_return_proper_description(self):
        response = self.api_session.get("/@types/Link")
        res = response.json()

        self.assertEqual(
            res["properties"]["remoteUrl"]["description"],
            "Insert an external link directly into the field,or select an internal link clicking on the icon.",  # noqa
        )
