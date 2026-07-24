# -*- coding: utf-8 -*-
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from redturtle.volto.testing import REDTURTLE_VOLTO_API_FUNCTIONAL_TESTING
from uuid import uuid4

import unittest


class LinkCheckerToolTest(unittest.TestCase):
    layer = REDTURTLE_VOLTO_API_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()

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
        # a stale entry from a previous run must be pruned by check_site
        from datetime import datetime

        self.tool._outgoing_links["stale-uid"] = (datetime.now(), [])

        self.tool.check_site()
        self.assertNotEqual(self.tool._last_update, None)
        self.assertNotIn("stale-uid", self.tool._outgoing_links)
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

    def test_any_2xx_status_is_not_broken(self):
        from datetime import datetime

        self.tool._outgoing_links[self.document.UID()] = (
            datetime.now(),
            [
                ("https://example.com/ok", 200),
                ("https://example.com/accepted", 202),
                ("https://example.com/broken", 404),
            ],
        )
        broken_links = dict(self.tool.get_page_with_broken_links())
        self.assertEqual(
            broken_links[self.document.UID()],
            [("https://example.com/broken", 404)],
        )
        rows = list(self.tool.get_rows(broken=True))
        self.assertEqual(len(rows), 2)  # header + the 404 row

    def test_deleted_content_is_skipped_in_report(self):
        from datetime import datetime

        # a UID that does not resolve to any content (deleted after the check)
        self.tool._outgoing_links["gone-uid"] = (
            datetime.now(),
            [("https://example.com/broken", 404)],
        )
        broken_links = dict(self.tool.get_page_with_broken_links())
        self.assertNotIn("gone-uid", broken_links)
        rows = list(self.tool.get_rows(broken=True))
        self.assertEqual(len(rows), 1)  # header only, the gone content is skipped

    def test_bot_protected_links_are_not_broken(self):
        from datetime import datetime

        self.tool._outgoing_links[self.document.UID()] = (
            datetime.now(),
            [
                ("https://linkedin.com/x", 999),  # LinkedIn anti-bot
                ("https://foo.com/forbidden", 403),
                ("https://foo.com/throttled", 429),
                ("https://foo.com/broken", 404),
            ],
        )
        # only the real 404 is reported as broken
        broken_links = dict(self.tool.get_page_with_broken_links())
        self.assertEqual(
            broken_links[self.document.UID()],
            [("https://foo.com/broken", 404)],
        )
        # the blocked ones still show in the csv, with a dedicated description
        rows = list(self.tool.get_rows(broken=True))
        blocked = [r for r in rows if r[3] == 999]
        self.assertEqual(len(blocked), 1)
        self.assertIn("Blocked by bot protection", blocked[0][4])

    def test_broken_http_link_working_on_https(self):
        from redturtle.volto.linkchecker import STATUS_HTTPS_ONLY

        class FakeResponse:
            def __init__(self, status_code):
                self.status_code = status_code
                self.headers = {}

            def close(self):
                pass

        class FakeSession:
            def __init__(self, statuses):
                self.statuses = statuses

            def head(self, url, **kwargs):
                return FakeResponse(self.statuses[url])

            get = head

        # http broken, https works -> flagged as "update to https"
        session = FakeSession({"http://foo.com/bar": 400, "https://foo.com/bar": 200})
        self.assertEqual(
            self.tool._fetch_status(
                "http://foo.com/bar", timeout=1, headers={}, session=session
            ),
            STATUS_HTTPS_ONLY,
        )

        # broken on both protocols -> keep the original status
        session = FakeSession({"http://foo.com/bar": 400, "https://foo.com/bar": 404})
        self.assertEqual(
            self.tool._fetch_status(
                "http://foo.com/bar", timeout=1, headers={}, session=session
            ),
            400,
        )
