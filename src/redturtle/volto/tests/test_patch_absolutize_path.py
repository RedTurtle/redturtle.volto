# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from Products.CMFPlone.controlpanel.browser.redirects import absolutize_path
from redturtle.volto.testing import REDTURTLE_VOLTO_INTEGRATION_TESTING

import unittest


class TestAbsolutizePath(unittest.TestCase):
    """ """

    layer = REDTURTLE_VOLTO_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.foo = api.content.create(
            container=self.portal,
            type="Document",
            title="Foo",
        )

    def test_patched_method_allows_to_create_alias_with_same_path(self):
        # by default will return
        # ('/plone/foo/foo', 'Cannot use a working path as alternative url.')
        self.assertEqual(absolutize_path("/foo/foo"), ("/plone/foo/foo", None))
