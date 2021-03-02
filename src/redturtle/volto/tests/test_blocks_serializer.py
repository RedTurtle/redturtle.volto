# -*- coding: utf-8 -*-
from plone import api
from plone.app.testing import (
    SITE_OWNER_NAME,
    SITE_OWNER_PASSWORD,
    TEST_USER_ID,
    setRoles,
)
from plone.restapi.testing import RelativeSession
from redturtle.volto.testing import REDTURTLE_VOLTO_API_FUNCTIONAL_TESTING
from transaction import commit
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.interfaces import ISerializeToJson
from zope.component import getMultiAdapter

import unittest


class TestBlocksSerializer(unittest.TestCase):

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

    def test_blocks_internal_refs_with_uid_get_serialized(self):

        self.page_a.blocks = {
            "foo": {
                "@type": "custom_block",
                "field": [{"UID": self.page_b.UID()}],
            },
        }
        commit()
        response = self.api_session.get(self.page_a.absolute_url())

        res = response.json()
        self.assertEqual(
            res["blocks"]["foo"]["field"][0],
            getMultiAdapter((self.page_b, self.request), ISerializeToJson)(),
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

        res = response.json()
        self.assertEqual(
            res["blocks"]["foo"]["field"][0],
            getMultiAdapter(
                (self.page_a, self.request), ISerializeToJsonSummary
            )(),
        )
