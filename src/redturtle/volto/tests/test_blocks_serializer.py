# -*- coding: utf-8 -*-
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.testing import RelativeSession
from redturtle.volto.testing import REDTURTLE_VOLTO_API_FUNCTIONAL_TESTING
from transaction import commit
from zope.component import getMultiAdapter

import unittest


class TestBlocksSerializer(unittest.TestCase):
    layer = REDTURTLE_VOLTO_API_FUNCTIONAL_TESTING
    maxDiff = None

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

        self.page_a = api.content.create(
            container=self.portal, type="Document", title="Page A"
        )

        self.page_b = api.content.create(
            container=self.portal, type="Document", title="Page B"
        )

        self.page_c = api.content.create(
            container=self.portal, type="Document", title="Page C"
        )

        commit()

    def tearDown(self):
        self.api_session.close()

    def test_blocks_internal_refs_with_uid_get_serialized_as_summary(self):
        self.page_a.blocks = {
            "foo": {
                "@type": "custom_block",
                "field": [{"UID": self.page_b.UID()}],
            },
        }
        commit()
        response = self.api_session.get(self.page_a.absolute_url())
        brain = api.content.find(UID=self.page_b.UID())[0]
        res = response.json()
        self.assertEqual(
            res["blocks"]["foo"]["field"][0],
            getMultiAdapter((brain, self.request), ISerializeToJsonSummary)(
                force_all_metadata=True
            ),
        )

    def test_blocks_internal_refs_dont_generate_recursion_depth(self):
        self.page_a.blocks = {
            "foo": {
                "@type": "custom_block",
                "field": [{"UID": self.page_a.UID()}],
            },
        }
        commit()
        response = self.api_session.get(self.page_a.absolute_url())
        brain = api.content.find(UID=self.page_a.UID())[0]
        res = response.json()
        self.assertEqual(
            res["blocks"]["foo"]["field"][0],
            getMultiAdapter((brain, self.request), ISerializeToJsonSummary)(
                force_all_metadata=True
            ),
        )


class TestRepeatableBlockSerializer(unittest.TestCase):
    layer = REDTURTLE_VOLTO_API_FUNCTIONAL_TESTING
    maxDiff = None

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)
        self.api_session_anon = RelativeSession(self.portal_url)
        self.api_session_anon.headers.update({"Accept": "application/json"})

        self.page_a = api.content.create(
            container=self.portal, type="Document", title="Page A"
        )

        self.page_b = api.content.create(
            container=self.portal, type="Document", title="Page B"
        )

        self.link = api.content.create(
            container=self.portal,
            type="Link",
            title="Link",
            remoteUrl="https://www.plone.org",
        )

        api.content.transition(obj=self.page_a, transition="publish")
        api.content.transition(obj=self.page_b, transition="publish")
        api.content.transition(obj=self.link, transition="publish")
        commit()

    def tearDown(self):
        self.api_session.close()
        self.api_session_anon.close()

    def test_repeatableContentBlock_serialize_href_with_referenced_obj_for_admin(self):
        self.page_a.blocks = {
            "foo": {
                "@type": "repeatableContentBlock",
                "href": f"resolveuid/{self.page_b.UID()}",
            },
        }
        commit()
        response = self.api_session.get(self.page_a.absolute_url())
        res = response.json()
        self.assertEqual(res["blocks"]["foo"]["href"], self.page_b.absolute_url())

    def test_repeatableContentBlock_serialize_href_with_referenced_obj_for_anon(self):
        self.page_a.blocks = {
            "foo": {
                "@type": "repeatableContentBlock",
                "href": f"resolveuid/{self.page_b.UID()}",
            },
        }
        commit()
        response = self.api_session_anon.get(self.page_a.absolute_url())
        res = response.json()
        self.assertEqual(res["blocks"]["foo"]["href"], self.page_b.absolute_url())

    def test_repeatableContentBlock_serialize_href_with_referenced_link_obj_for_admin(
        self,
    ):
        self.page_a.blocks = {
            "foo": {
                "@type": "repeatableContentBlock",
                "href": f"resolveuid/{self.link.UID()}",
            },
        }
        commit()
        response = self.api_session.get(self.page_a.absolute_url())
        res = response.json()
        self.assertEqual(res["blocks"]["foo"]["href"], self.link.absolute_url())

    def test_repeatableContentBlock_serialize_href_with_referenced_link_obj_for_anon(
        self,
    ):
        self.page_a.blocks = {
            "foo": {
                "@type": "repeatableContentBlock",
                "href": f"resolveuid/{self.link.UID()}",
            },
        }
        commit()
        response = self.api_session_anon.get(self.page_a.absolute_url())
        res = response.json()
        self.assertEqual(res["blocks"]["foo"]["href"], self.link.absolute_url())
