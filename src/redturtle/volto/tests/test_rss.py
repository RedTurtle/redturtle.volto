# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from redturtle.volto.testing import REDTURTLE_VOLTO_API_FUNCTIONAL_TESTING

import unittest


class TestContentTypeLink(unittest.TestCase):
    layer = REDTURTLE_VOLTO_API_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.news1 = api.content.create(
            container=self.portal,
            type="News Item",
            title="News 1",
            description="",
        )
        self.news2 = api.content.create(
            container=self.portal,
            type="News Item",
            title="News 2",
            description="",
        )

    def test_rss_item(self):
        import pdb

        pdb.set_trace()
