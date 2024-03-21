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
            doc = api.content.create(
                container=self.portal,
                type="Document",
                title=f"Document {i}",
            )
            api.content.transition(obj=doc, transition="publish")
        commit()

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

        self.api_session_anon = RelativeSession(self.portal_url)
        self.api_session_anon.headers.update({"Accept": "application/json"})

    def tearDown(self):
        self.api_session.close()
        self.api_session_anon.close()

    def test_search_b_size_not_limited_for_auth(self):
        response = self.api_session.get(
            "/@search", params={"portal_type": "Document", "b_size": 1000}
        )
        result = response.json()
        self.assertEqual(len(result["items"]), self.MAX_LIMIT + 1)

    def test_querystringsearch_post_not_limited_for_auth(self):
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
        self.assertEqual(len(result["items"]), self.MAX_LIMIT + 1)
        self.assertEqual(result["items_total"], self.MAX_LIMIT + 1)

    def test_querystringsearch_get_not_limited_for_auth(self):
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
        self.assertEqual(len(result["items"]), self.MAX_LIMIT + 1)
        self.assertEqual(result["items_total"], self.MAX_LIMIT + 1)

    def test_search_b_size_default_to_500_for_anon(self):
        response = self.api_session_anon.get(
            "/@search", params={"portal_type": "Document", "b_size": 1000}
        )
        result = response.json()
        self.assertEqual(len(result["items"]), self.MAX_LIMIT)

    def test_querystringsearch_post_default_limit_500_for_anon(self):
        response = self.api_session_anon.post(
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

    def test_querystringsearch_get_default_limit_500_for_anon(self):
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
        response = self.api_session_anon.get(
            f"/@querystring-search?query={quote(json.dumps(query))}",
        )

        result = response.json()
        self.assertEqual(len(result["items"]), self.MAX_LIMIT)
        self.assertEqual(result["items_total"], self.MAX_LIMIT)
