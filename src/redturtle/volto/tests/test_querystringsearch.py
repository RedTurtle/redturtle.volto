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


class TestQuerystringSearch(unittest.TestCase):
    layer = REDTURTLE_VOLTO_API_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()

        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        api.content.create(container=self.portal, type="Document", title="First")
        api.content.create(container=self.portal, type="Document", title="Second")
        commit()

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

    def tearDown(self):
        self.api_session.close()

    def test_do_not_return_random_item_in_objectbrowser_call_if_absolutePath_is_invalid(
        self,
    ):
        """
        objectbrowser calls always ask for an absolutePath adn b_size == 1.
        absolutePath is the uid of the referenced object
        """
        response = self.api_session.post(
            "/@querystring-search",
            json={
                "query": [
                    {
                        "i": "path",
                        "o": "plone.app.querystring.operation.string.absolutePath",
                        "v": "xxx::1",
                    }
                ],
                "b_size": 1,
            },
        )
        result = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(result["error"]["message"], "No query supplied")

    def test_if_absolutePath_is_invalid_and_is_not_a_objectbrowser_call_do_not_filter_by_path(
        self,
    ):
        """
        objectbrowser calls always ask for an absolutePath adn b_size == 1.
        absolutePath is the uid of the referenced object.
        By default Plone (querystringsearch) set /Plone as query path if absolutePath is invalid
        """
        response = self.api_session.post(
            "/@querystring-search",
            json={
                "query": [
                    {
                        "i": "path",
                        "o": "plone.app.querystring.operation.string.absolutePath",
                        "v": "xxx::1",
                    }
                ],
            },
        )
        result = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(result["items_total"], 2)
