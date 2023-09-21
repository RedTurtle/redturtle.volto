# -*- coding: utf-8 -*-
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.restapi.testing import RelativeSession
from redturtle.volto.testing import REDTURTLE_VOLTO_API_FUNCTIONAL_TESTING
from transaction import commit
from urllib.parse import quote

import json
import unittest


class CatalogLimitPatches(unittest.TestCase):
    layer = REDTURTLE_VOLTO_API_FUNCTIONAL_TESTING
    MAX_LIMIT = 500

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()

        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        for i in range(self.MAX_LIMIT + 1):
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

    def test_search_b_size_default_to_500(self):
        response = self.api_session.get(
            "/@search", params={"portal_type": "Document", "b_size": 1000}
        )
        result = response.json()
        self.assertEqual(len(result["items"]), self.MAX_LIMIT)

    def test_querystringsearch_post_default_limit_500(self):
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
        self.assertEqual(len(result["items"]), self.MAX_LIMIT)
        self.assertEqual(result["items_total"], self.MAX_LIMIT)

    def test_querystringsearch_get_default_limit_500(self):
        query = {
            "query": [
                {
                    "i": "portal_type",
                    "o": "plone.app.querystring.operation.selection.any",
                    "v": ["Document"],
                }
            ],
            "b_size": 2000,
            "limit": 2000,
        }
        response = self.api_session.get(
            f"/@querystring-search?query={quote(json.dumps(query))}",
        )

        result = response.json()
        self.assertEqual(len(result["items"]), self.MAX_LIMIT)
        self.assertEqual(result["items_total"], self.MAX_LIMIT)
