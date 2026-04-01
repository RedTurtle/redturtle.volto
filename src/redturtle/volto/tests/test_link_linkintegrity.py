# -*- coding: utf-8 -*-
from plone import api
from plone.app.linkintegrity.utils import getIncomingLinks
from plone.app.linkintegrity.utils import getOutgoingLinks
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from redturtle.volto.testing import REDTURTLE_VOLTO_INTEGRATION_TESTING

import unittest


class TestLinkLinkintegrity(unittest.TestCase):
    layer = REDTURTLE_VOLTO_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

    def test_link_to_object_generate_reference(self):
        doc = api.content.create(container=self.portal, type="Document", title="doc")

        self.assertEqual(len(list(getIncomingLinks(doc))), 0)

        link = api.content.create(
            container=self.portal,
            type="Link",
            title="link",
            remoteUrl=f"${{portal_url}}/resolveuid/{doc.UID()}",
        )
        self.assertEqual(len(list(getIncomingLinks(doc))), 1)
        self.assertEqual([x.from_object for x in getIncomingLinks(doc)], [link])

        self.assertEqual(len(list(getOutgoingLinks(link))), 1)
        self.assertEqual([x.to_object for x in getOutgoingLinks(link)], [doc])

    def test_link_to_external_do_not_generate_reference(self):
        doc = api.content.create(container=self.portal, type="Document", title="doc")

        self.assertEqual(len(list(getIncomingLinks(doc))), 0)

        link = api.content.create(
            container=self.portal,
            type="Link",
            title="link",
            remoteUrl="https://www.plone.org",
        )
        self.assertEqual(len(list(getIncomingLinks(doc))), 0)

        self.assertEqual(len(list(getOutgoingLinks(link))), 0)
