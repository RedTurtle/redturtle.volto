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
        # a site-root object whose id is equal to the texts used below
        api.content.create(
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

    def test_simple_card_title_equal_to_object_id_is_not_converted(self):
        block = self.patch_block(
            {"@type": "testo_riquadro_semplice", "simple_card_title": "titolo"}
        )
        self.assertEqual(block["simple_card_title"], "titolo")

    def test_subblocks_title_equal_to_object_id_is_not_converted(self):
        block = self.patch_block(
            {"@type": "iconBlocks", "subblocks": [{"id": "abc", "title": "titolo"}]}
        )
        self.assertEqual(block["subblocks"][0]["title"], "titolo")
