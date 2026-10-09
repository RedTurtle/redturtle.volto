from plone import api
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.restapi.testing import RelativeSession
from redturtle.volto.testing import REDTURTLE_VOLTO_API_FUNCTIONAL_TESTING
from transaction import commit

import unittest


class TestGenericBlocksDeserializer(unittest.TestCase):
    layer = REDTURTLE_VOLTO_API_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

        self.document = api.content.create(
            container=self.portal, type="Document", title="Page"
        )
        self.ref = api.content.create(
            container=self.portal, type="Document", id="titolo", title="Titolo"
        )
        commit()

    def tearDown(self):
        self.api_session.close()

    def patch_block(self, block):
        response = self.api_session.patch(
            self.document.absolute_url(), json={"blocks": {"xyz": block}}
        )
        self.assertEqual(response.status_code, 204)
        commit()
        return self.document.blocks["xyz"]

    def test_plain_text_equal_to_object_id_is_not_converted(self):
        block = self.patch_block({"@type": "custom_block", "title": "titolo"})
        self.assertEqual(block["title"], "titolo")

    def test_plain_text_in_list_equal_to_object_id_is_not_converted(self):
        block = self.patch_block({"@type": "custom_block", "items": ["titolo"]})
        self.assertEqual(block["items"], ["titolo"])

    def test_paths_and_urls_are_converted_to_resolveuid(self):
        block = self.patch_block(
            {
                "@type": "custom_block",
                "path": "/titolo",
                "url": f"{self.portal_url}/titolo",
                "items": ["/titolo"],
            }
        )
        resolveuid = f"../resolveuid/{self.ref.UID()}"
        self.assertEqual(block["path"], resolveuid)
        self.assertEqual(block["url"], resolveuid)
        self.assertEqual(block["items"], [resolveuid])
