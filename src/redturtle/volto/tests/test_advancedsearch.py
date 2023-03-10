# -*- coding: utf-8 -*-
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.restapi.testing import RelativeSession
from redturtle.volto.testing import REDTURTLE_VOLTO_API_FUNCTIONAL_TESTING
from transaction import commit

import unittest


class AdvancedSearchTest(unittest.TestCase):

    layer = REDTURTLE_VOLTO_API_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()

        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        # 2nd for "Foo" (title + description + searchableText)
        # 3rd for "Bar" (description + searchableText)
        # 2nd for "Foo Bar" (description + searchableText)
        api.content.create(
            container=self.portal,
            type="Folder",
            id="f1",
            title="Foo folder",
            description="Foo Bar",
        )
        # 1st for "Foo" (title + description + subject + searchableText)
        # 1st for "Bar" (subject + searchableText)
        # 3rd for "Foo Bar" (searchableText)
        api.content.create(
            container=self.portal,
            type="Document",
            id="d1",
            title="document",
            description="Foo document",
            subject=["foo", "bar"],
        )
        # 3rd for "Foo" (title + searchableText)
        # 2nd for "Bar" (title + searchableText)
        # 1st for "Foo Bar" (title + searchableText)
        api.content.create(
            container=self.portal,
            type="Event",
            id="e1",
            title="Foo Bar event",
        )
        commit()

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

    def test_simplesearch(self):
        response = self.api_session.get(
            "/@search", params={"SearchableText": "foo", "SimpleQuery.": True}
        )
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(result["items_total"], 3)
        # explain why the order is different from the one in the test above
        self.assertEqual(
            ["f1", "d1", "e1"], [item["@id"].split("/")[-1] for item in result["items"]]
        )

    def test_search_foo(self):
        response = self.api_session.get("/@search", params={"SearchableText": "foo"})
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(result["items_total"], 3)
        self.assertEqual(
            ["d1", "f1", "e1"], [item["@id"].split("/")[-1] for item in result["items"]]
        )

    def test_search_foo_bar(self):
        response = self.api_session.get(
            "/@search", params={"SearchableText": "foo bar"}
        )
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(result["items_total"], 3)
        self.assertEqual(
            ["e1", "f1", "d1"], [item["@id"].split("/")[-1] for item in result["items"]]
        )

    def test_search_bar(self):
        response = self.api_session.get("/@search", params={"SearchableText": "bar"})
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(result["items_total"], 3)
        self.assertEqual(
            ["d1", "e1", "f1"], [item["@id"].split("/")[-1] for item in result["items"]]
        )

    def test_search_document(self):
        response = self.api_session.get("/@search", params={"SearchableText": "bar", "portal_type": ["Document"]})
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(result["items_total"], 1)
        self.assertEqual(
            ["d1"], [item["@id"].split("/")[-1] for item in result["items"]]
        )
