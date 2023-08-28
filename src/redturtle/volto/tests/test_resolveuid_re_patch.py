# -*- coding: utf-8 -*-
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.restapi.serializer.utils import uid_to_url
from redturtle.volto.testing import REDTURTLE_VOLTO_FUNCTIONAL_TESTING

import unittest


class TestRESOLVEUIDREPatch(unittest.TestCase):
    layer = REDTURTLE_VOLTO_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()

        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.document = api.content.create(
            container=self.portal,
            type="Document",
            title="Document",
        )

    def test_uuid_to_url_with_link_pattern(self):
        path = f"/Plone/resolveuid/{self.document.UID()}"

        res = uid_to_url(path)
        self.assertEqual(res, self.document.absolute_url())

    def test_uuid_to_url_with_link_pattern_with_suffix(self):
        path = f"/Plone/resolveuid/{self.document.UID()}/@@download/file"

        res = uid_to_url(path)
        self.assertEqual(res, f"{self.document.absolute_url()}/@@download/file")
