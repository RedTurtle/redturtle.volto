# -*- coding: utf-8 -*-
"""Setup tests for this package."""

from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.restapi.testing import RelativeSession
from redturtle.volto.testing import REDTURTLE_VOLTO_API_FUNCTIONAL_TESTING

import unittest


class TestCreation(unittest.TestCase):
    layer = REDTURTLE_VOLTO_API_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

    def test_fix_id_if_contains_spaces(self):
        """Test that id with spaces is fixed"""

        response = self.api_session.post(
            self.portal_url,
            json={
                "@type": "Document",
                "title": "My doc",
                "id": "aa bb",
            },
        )
        self.assertEqual(response.json()["id"], "aa-bb")

        obj_url = response.json()["@id"]
        response = self.api_session.patch(
            obj_url,
            json={"id": "aa bb"},
        )

        self.assertEqual(response.status_code, 204)

        response = self.api_session.get(
            obj_url,
        )

        self.assertEqual(response.json()["id"], "aa-bb-1")

    def test_fix_id_if_contains_invalid_chars(self):
        """Test that id with invalid chars is fixed"""

        response = self.api_session.post(
            self.portal_url,
            json={
                "@type": "Document",
                "title": "My doc",
                "id": "aàbbù",
            },
        )

        self.assertEqual(response.status_code, 201)
