# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.restapi.testing import RelativeSession
from redturtle.volto.testing import REDTURTLE_VOLTO_API_FUNCTIONAL_TESTING
from transaction import commit

import unittest


class TestContentTypeLink(unittest.TestCase):
    layer = REDTURTLE_VOLTO_API_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)
        self.api_session_anon = RelativeSession(self.portal_url)
        self.api_session_anon.headers.update({"Accept": "application/json"})

        self.private_page = api.content.create(
            container=self.portal, type="Document", title="Private page"
        )
        self.public_page = api.content.create(
            container=self.portal, type="Document", title="Public page"
        )

        self.link_with_public_page = api.content.create(
            container=self.portal,
            type="Link",
            title="Link with public page",
            remoteUrl="/plone/resolveuid/{}".format(self.public_page.UID()),
        )
        self.link_with_private_page = api.content.create(
            container=self.portal,
            type="Link",
            title="Link with private page",
            remoteUrl="/plone/resolveuid/{}".format(self.private_page.UID()),
        )

        self.link_with_external_page = api.content.create(
            container=self.portal,
            type="Link",
            title="Link with public page",
            remoteUrl="https://plone.org",
        )

        api.content.transition(obj=self.public_page, transition="publish")
        api.content.transition(obj=self.link_with_private_page, transition="publish")
        api.content.transition(obj=self.link_with_public_page, transition="publish")
        api.content.transition(obj=self.link_with_external_page, transition="publish")
        commit()

    def tearDown(self):
        self.api_session.close()
        self.api_session_anon.close()

    def test_admin_always_have_remoteUrl_info_for_internal_links(self):
        response = self.api_session.get(
            "/@search?portal_type=Link&metadata_fields=_all&sort_on=sortable_title"
        )
        res = response.json()

        self.assertEqual(res["items_total"], 3)
        self.assertIn(res["items"][0]["remoteUrl"], self.private_page.absolute_url())
        self.assertEqual(res["items"][1]["remoteUrl"], self.public_page.absolute_url())
        self.assertEqual(res["items"][2]["remoteUrl"], "https://plone.org")

    def test_anon_can_see_internal_link_even_if_cant_access_to_it(
        self,
    ):
        response = self.api_session_anon.get(
            "/@search?portal_type=Link&metadata_fields=_all&sort_on=sortable_title"
        )
        res = response.json()
        self.assertEqual(res["items_total"], 3)
        self.assertEqual(res["items"][0]["remoteUrl"], self.private_page.absolute_url())
        self.assertIn(res["items"][1]["remoteUrl"], self.public_page.absolute_url())

    def test_anon_can_access_to_external_links(self):
        response = self.api_session_anon.get(
            "/@search?portal_type=Link&metadata_fields=_all&sort_on=sortable_title"
        )
        res = response.json()
        self.assertEqual(res["items_total"], 3)
        self.assertIn(res["items"][2]["remoteUrl"], "https://plone.org")

    def test_there_are_two_similar_metadata(self):
        response = self.api_session_anon.get(
            "/@search?portal_type=Link&metadata_fields=_all&sort_on=sortable_title"
        )
        res = response.json()
        self.assertEqual(res["items_total"], 3)
        self.assertIn("remoteUrl", res["items"][0].keys())
        self.assertIn("getRemoteUrl", res["items"][0].keys())

        self.assertEqual(res["items"][0]["remoteUrl"], res["items"][0]["getRemoteUrl"])
        self.assertEqual(res["items"][1]["remoteUrl"], res["items"][1]["getRemoteUrl"])
        self.assertEqual(res["items"][2]["remoteUrl"], res["items"][2]["getRemoteUrl"])
