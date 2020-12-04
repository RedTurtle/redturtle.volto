# -*- coding: utf-8 -*-
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.registry.interfaces import IRegistry
from plone.restapi.testing import RelativeSession
from Products.CMFPlone.interfaces import ISearchSchema
from redturtle.volto.testing import REDTURTLE_VOLTO_API_FUNCTIONAL_TESTING
from transaction import commit
from zope.component import getUtility

import unittest


class SiteSearchTest(unittest.TestCase):

    layer = REDTURTLE_VOLTO_API_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        api.content.create(container=self.portal, type="Folder", title="Foo folder")
        api.content.create(container=self.portal, type="Document", title="Foo document")
        api.content.create(container=self.portal, type="Event", title="Foo event")

    def test_route_exists(self):
        response = self.api_session.get("/@site-search")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get("Content-Type"), "application/json")

    def test_types_not_searched(self):
        registry = getUtility(IRegistry)
        search_settings = registry.forInterface(ISearchSchema, prefix="plone")
        search_settings.types_not_searched = ("Folder",)
        commit()

        response = self.api_session.get("/@site-search")
        result = response.json()

        self.assertEqual(result["items_total"], 2)
        titles = [x["title"] for x in result["items"]]
        self.assertEqual(["Foo document", "Foo event"], titles)
