# -*- coding: utf-8 -*-
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.restapi.testing import RelativeSession
from redturtle.volto.testing import REDTURTLE_VOLTO_API_FUNCTIONAL_TESTING
from transaction import commit
from redturtle.volto.restapi.services.search.get import MAX_LIMIT

import unittest


class CatalogLimitPatches(unittest.TestCase):
    layer = REDTURTLE_VOLTO_API_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()

        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        for i in range(210):
            api.content.create(
                container=self.portal,
                type="Document",
                title=f"Document {i}",
            )
        commit()

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

    def tearDown(self):
        self.api_session.close()

    def test_search_b_size_to_200(self):
        response = self.api_session.get(
            "/@search", params={"portal_type": "Document", "b_size": 1000}
        )
        result = response.json()
        self.assertEqual(len(result["items"]), MAX_LIMIT)

    def test_querystringsearch_post_limit_200(self):
        response = self.api_session.post(
            "/@querystring-search",
            json={
                "query": [
                    {
                        "i": "portal_type",
                        "o": "plone.app.querystring.operation.selection.is",
                        "v": ["Document"],
                    }
                ],
                "limit": 2000,
                "b_size": 2000,
            },
        )
        result = response.json()
        self.assertEqual(len(result["items"]), MAX_LIMIT)
        self.assertEqual(result["items_total"], MAX_LIMIT)

    def test_querystringsearch_get_limit_200(self):
        response = self.api_session.get(
            "/@querystring-search?query=%7B%22query%22%3A%20%5B%7B%22i%22%3A%20%22portal_type%22%2C%20%22o%22%3A%20%22plone.app.querystring.operation.selection.any%22%2C%20%22v%22%3A%20%5B%22Document%22%5D%7D%5D%2C%20%22b_size%22%3A%202000%2C%20%22limit%22%3A%202000%7D",
        )
        result = response.json()
        self.assertEqual(len(result["items"]), MAX_LIMIT)
        self.assertEqual(result["items_total"], MAX_LIMIT)
