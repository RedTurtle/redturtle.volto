from plone import api
from plone.app.layout.navigation.interfaces import INavigationRoot
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.services.navroot.get import Navroot as BaseNavroot
from plone.restapi.testing import RelativeSession
from redturtle.volto.interfaces import IRedturtleVoltoLayer
from redturtle.volto.restapi.services.navroot.get import Navroot
from redturtle.volto.testing import REDTURTLE_VOLTO_API_FUNCTIONAL_TESTING
from zope.component import getMultiAdapter
from zope.interface import alsoProvides
from zope.interface import noLongerProvides

import transaction
import unittest

SITE_BLOCKS = {
    "site-title": {"@type": "title"},
    "site-text": {"@type": "slate", "plaintext": "site root text"},
}
SITE_BLOCKS_LAYOUT = {"items": ["site-title", "site-text"]}

SUBSITE_BLOCKS = {
    "subsite-title": {"@type": "title"},
    "subsite-text": {"@type": "slate", "plaintext": "subsite text"},
}
SUBSITE_BLOCKS_LAYOUT = {"items": ["subsite-title", "subsite-text"]}


class TestServiceNavroot(unittest.TestCase):
    layer = REDTURTLE_VOLTO_API_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

        self.portal.blocks = SITE_BLOCKS
        self.portal.blocks_layout = SITE_BLOCKS_LAYOUT

        self.page = api.content.create(
            container=self.portal, type="Document", title="Page"
        )
        self.page.blocks = {"page-title": {"@type": "title"}}
        self.page.blocks_layout = {"items": ["page-title"]}

        self.subsite = api.content.create(
            container=self.portal, type="Document", title="Subsite"
        )
        self.subsite.blocks = SUBSITE_BLOCKS
        self.subsite.blocks_layout = SUBSITE_BLOCKS_LAYOUT
        alsoProvides(self.subsite, INavigationRoot)

        transaction.commit()

    def tearDown(self):
        self.api_session.close()

    def test_site_root_has_blocks(self):
        # sanity check: the site root really has blocks, so their absence
        # in @navroot is not a coincidence.
        response = self.api_session.get("/")
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(result["blocks_layout"], SITE_BLOCKS_LAYOUT)
        self.assertIn("site-text", result["blocks"])

    def test_navroot_endpoint_on_site_root_has_no_blocks(self):
        response = self.api_session.get("/@navroot")
        self.assertEqual(response.status_code, 200)
        navroot = response.json()["navroot"]

        self.assertEqual(navroot["@id"], self.portal_url)
        self.assertEqual(navroot["title"], self.portal.title)
        self.assertNotIn("blocks", navroot)
        self.assertNotIn("blocks_layout", navroot)

    def test_navroot_endpoint_on_navigation_root_has_no_blocks(self):
        response = self.api_session.get("/subsite/@navroot")
        self.assertEqual(response.status_code, 200)
        navroot = response.json()["navroot"]

        self.assertEqual(navroot["@id"], self.subsite.absolute_url())
        self.assertEqual(navroot["title"], "Subsite")
        self.assertNotIn("blocks", navroot)
        self.assertNotIn("blocks_layout", navroot)

    def test_navroot_expander_has_no_blocks(self):
        response = self.api_session.get("/page", params={"expand": "navroot"})
        self.assertEqual(response.status_code, 200)
        result = response.json()

        # blocks of the main content are still there
        self.assertIn("page-title", result["blocks"])
        self.assertEqual(result["blocks_layout"], {"items": ["page-title"]})

        navroot = result["@components"]["navroot"]["navroot"]
        self.assertEqual(navroot["@id"], self.portal_url)
        self.assertEqual(navroot["title"], self.portal.title)
        self.assertNotIn("blocks", navroot)
        self.assertNotIn("blocks_layout", navroot)

    def test_navroot_expander_on_navigation_root_itself_has_no_blocks(self):
        # homepage case: the context is the navigation root, so without the
        # customization its blocks would be returned twice.
        response = self.api_session.get("/subsite", params={"expand": "navroot"})
        self.assertEqual(response.status_code, 200)
        result = response.json()

        self.assertEqual(result["blocks_layout"], SUBSITE_BLOCKS_LAYOUT)
        self.assertIn("subsite-text", result["blocks"])

        navroot = result["@components"]["navroot"]["navroot"]
        self.assertEqual(navroot["@id"], self.subsite.absolute_url())
        self.assertEqual(navroot["title"], "Subsite")
        self.assertNotIn("blocks", navroot)
        self.assertNotIn("blocks_layout", navroot)

    def test_navroot_expander_not_expanded(self):
        response = self.api_session.get("/page")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["@components"]["navroot"],
            {"@id": f"{self.portal_url}/page/@navroot"},
        )

    def test_layer_adapter_wins_over_plone_restapi_one(self):
        # without the layer, plone.restapi adapter is used and blocks are there
        noLongerProvides(self.request, IRedturtleVoltoLayer)
        adapter = getMultiAdapter(
            (self.subsite, self.request), IExpandableElement, name="navroot"
        )
        self.assertNotIsInstance(adapter, Navroot)
        self.assertIsInstance(adapter, BaseNavroot)
        navroot = adapter(expand=True)["navroot"]["navroot"]
        self.assertIn("blocks", navroot)
        self.assertIn("blocks_layout", navroot)

        # with the layer, redturtle.volto adapter is used and blocks are gone
        alsoProvides(self.request, IRedturtleVoltoLayer)
        adapter = getMultiAdapter(
            (self.subsite, self.request), IExpandableElement, name="navroot"
        )
        self.assertIsInstance(adapter, Navroot)
        navroot = adapter(expand=True)["navroot"]["navroot"]
        self.assertEqual(navroot["@id"], self.subsite.absolute_url())
        self.assertNotIn("blocks", navroot)
        self.assertNotIn("blocks_layout", navroot)
