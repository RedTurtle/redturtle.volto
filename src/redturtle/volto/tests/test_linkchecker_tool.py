# -*- coding: utf-8 -*-
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.restapi.testing import RelativeSession
from redturtle.volto.testing import REDTURTLE_VOLTO_API_FUNCTIONAL_TESTING
from uuid import uuid4

import unittest


class LinkCheckerToolTest(unittest.TestCase):
    layer = REDTURTLE_VOLTO_API_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        api.content.create(container=self.portal, type="Folder", title="Foo folder")

        self.document = api.content.create(
            container=self.portal, type="Document", title="Foo document"
        )

        self.document.blocks = {
            "xyz": {
                "@type": "testo_riquadro_immagine",
                "image_card_title": {"blocks": [{"text": "imagetitle"}]},
                "image_card_content": {"blocks": [{"text": "imagetext"}]},
                "text": {
                    "blocks": [
                        {
                            "urls": [
                                "https://httpstat.us/404",  # broken
                                f"/resolveuid/{str(uuid4())}",  # broken
                                f"/resolveuid/{self.document.UID()}",  # internal ok
                            ]
                        }
                    ]
                },
            },
        }
        self.document.blocks_layout = {"items": ["xyz"]}

        api.content.create(container=self.portal, type="Event", title="Foo event")

        self.link_524 = api.content.create(
            container=self.portal,
            type="Link",
            title="Foo link 524",
            remoteUrl="https://httpstat.us/524",
        )
        self.link_404 = api.content.create(
            container=self.portal,
            type="Link",
            title="Foo link 404",
            remoteUrl="https://httpstat.us/404",
        )

        self.tool = api.portal.get_tool("portal_linkchecker")

    def test_tool_exists(self):
        self.assertTrue(self.tool)

    def test_clear(self):
        self.tool.clear()
        self.assertEqual(len(self.tool._external_links_status), 0)
        self.assertEqual(len(self.tool._outgoing_links), 0)
        self.assertEqual(self.tool._last_update, None)

    def test_check_site(self):
        self.tool.check_site()
        self.assertNotEqual(self.tool._last_update, None)
        self.assertEqual(len(self.tool._outgoing_links), 6)
        self.assertEqual(len(self.tool._external_links_status), 2)

        broken_links = {
            uid: links for (uid, links) in self.tool.get_page_with_broken_links()
        }
        self.assertEqual(len(broken_links), 3)
        self.assertIn(self.link_524.UID(), broken_links)
        self.assertIn(self.link_404.UID(), broken_links)
        self.assertIn(self.document.UID(), broken_links)
        self.assertEqual(len(broken_links[self.document.UID()]), 2)
