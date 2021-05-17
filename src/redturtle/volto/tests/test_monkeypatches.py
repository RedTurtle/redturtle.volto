# -*- coding: utf-8 -*-
import unittest
from Products.CMFPlone.interfaces import ISelectableConstrainTypes
from plone import api
from plone.app.testing import (
    TEST_USER_ID,
    setRoles,
)
from redturtle.volto.testing import REDTURTLE_VOLTO_FUNCTIONAL_TESTING


class TestRespectLocallyAllowedTypes(unittest.TestCase):

    layer = REDTURTLE_VOLTO_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.folder = api.content.create(
            container=self.portal,
            type="Folder",
            title="Folder",
            description="",
        )
        self.document = api.content.create(
            container=self.portal,
            type="Document",
            title="Page",
            description="",
        )
        self.news = api.content.create(
            container=self.portal,
            type="News Item",
            title="News",
            description="",
        )

    def test_cant_paste_with_filter_set(self):
        self.folder._verifyObjectPaste(self.document)

        constraints = ISelectableConstrainTypes(self.folder)
        constraints.setConstrainTypesMode(1)
        constraints.setLocallyAllowedTypes(("News Item",))

        self.assertRaises(
            ValueError, self.folder._verifyObjectPaste, self.document
        )
        self.folder._verifyObjectPaste(self.news)
