# -*- coding: utf-8 -*-
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.registry.interfaces import IRegistry
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.testing import RelativeSession
from redturtle.volto.testing import REDTURTLE_VOLTO_API_FUNCTIONAL_TESTING
from transaction import commit
from zope.component import getMultiAdapter
from zope.component import getUtility

import os
import unittest


class TestBlocksSerializer(unittest.TestCase):
    layer = REDTURTLE_VOLTO_API_FUNCTIONAL_TESTING
    maxDiff = None

    def setUp(self):
        tz = os.environ.get("TZ", "UTC")
        registry = getUtility(IRegistry)
        self._orig_tz = (
            registry["plone.portal_timezone"],
            registry["plone.available_timezones"],
        )
        registry["plone.portal_timezone"] = tz
        registry["plone.available_timezones"] = [tz]

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
        registry = getUtility(IRegistry)
        registry["plone.portal_timezone"] = self._orig_tz[0]
        registry["plone.available_timezones"] = self._orig_tz[1]

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
