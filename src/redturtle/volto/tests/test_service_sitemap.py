from plone import api
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.restapi.testing import RelativeSession
from redturtle.volto.interfaces import IRedTurtleVoltoSettings
from redturtle.volto.testing import REDTURTLE_VOLTO_API_FUNCTIONAL_TESTING
from transaction import commit

import unittest


class TestServicesSitemap(unittest.TestCase):
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

    def test_route_exists(self):
        response = self.api_session.get("/@sitemap-settings")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get("Content-Type"), "application/json")

    def test_return_values_from_registry(self):
        response = self.api_session.get("/@sitemap-settings")
        result = response.json()

        self.assertEqual(result["depth"], 3)

        api.portal.set_registry_record("plone.sitemap_depth", 5)
        commit()

        response = self.api_session.get("/@sitemap-settings")
        result = response.json()

        self.assertEqual(result["depth"], 5)

    def test_sitemap_returns_navigation_tree(self):
        folder = api.content.create(
            container=self.portal, type="Folder", id="folder", title="Folder"
        )
        api.content.create(container=folder, type="Document", id="doc", title="Doc")
        api.content.create(container=folder, type="Folder", id="sub", title="Sub")
        commit()

        def get_children():
            response = self.api_session.get("/@sitemap")
            self.assertEqual(response.status_code, 200)
            result = response.json()
            self.assertEqual(result["depth"], 3)
            top = [x for x in result["items"] if x["title"] == "Folder"][0]
            return sorted(x["title"] for x in top["items"])

        self.assertEqual(get_children(), ["Doc", "Sub"])

        api.portal.set_registry_record(
            "sitemap_page_excluded_types",
            ["Document"],
            interface=IRedTurtleVoltoSettings,
        )
        commit()

        self.assertEqual(get_children(), ["Sub"])

        # @navigation is not affected
        response = self.api_session.get(
            "/@navigation", params={"expand.navigation.depth": 3}
        )
        top = [x for x in response.json()["items"] if x["title"] == "Folder"][0]
        self.assertIn("Doc", [x["title"] for x in top["items"]])

    def test_sitemap_excludes_top_level_contents(self):
        api.content.create(
            container=self.portal, type="Document", id="root-doc", title="Root doc"
        )
        api.content.create(
            container=self.portal, type="Folder", id="root-folder", title="Root folder"
        )
        api.portal.set_registry_record(
            "sitemap_page_excluded_types",
            ["Document"],
            interface=IRedTurtleVoltoSettings,
        )
        commit()

        response = self.api_session.get("/@sitemap")
        titles = [x["title"] for x in response.json()["items"]]
        self.assertIn("Root folder", titles)
        self.assertNotIn("Root doc", titles)

        # @navigation is not affected
        response = self.api_session.get("/@navigation")
        titles = [x["title"] for x in response.json()["items"]]
        self.assertIn("Root doc", titles)
