# -*- coding: utf-8 -*-
import unittest

import transaction
from plone import api
from plone.app.testing import (
    TEST_USER_ID,
    setRoles,
)
from plone.restapi.testing import RelativeSession
from redturtle.volto.testing import REDTURTLE_VOLTO_API_FUNCTIONAL_TESTING


class TestVocabularyEndpoint(unittest.TestCase):

    layer = REDTURTLE_VOLTO_API_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        # create some test users
        api.user.create(
            username="member",
            email="member@example.org",
            password="secret",
            roles=("Member",),
        )
        api.user.create(
            username="contributor",
            email="contributor@example.org",
            password="secret",
            roles=("Member", "Contributor"),
        )

        api.user.create(
            username="editor",
            email="editor@example.org",
            password="secret",
            roles=("Member", "Editor", "Reviewer"),
        )

        # self.api_session = RelativeSession(self.portal_url)
        # self.api_session.headers.update({"Accept": "application/json"})
        # self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

        api.content.create(
            container=self.portal,
            type="Document",
            title="Page",
            description="",
            subject=["foo", "bar"],
        )

        transaction.commit()

    def test_anonymous_can_get_list_of_vocabularies(self):
        api_session = RelativeSession(self.portal_url)
        api_session.headers.update({"Accept": "application/json"})
        # api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)
        response = api_session.get("/@vocabularies")

        self.assertEqual(response.status_code, 200)

        api_session.close()

    def test_users_can_get_list_of_vocabularies(self):
        api_session = RelativeSession(self.portal_url)
        api_session.headers.update({"Accept": "application/json"})
        api_session.auth = ("member", "secret")
        response = api_session.get("/@vocabularies")

        self.assertEqual(response.status_code, 200)

        api_session.auth = ("contributor", "secret")
        response = api_session.get("/@vocabularies")

        self.assertEqual(response.status_code, 200)

        api_session.auth = ("editor", "secret")
        response = api_session.get("/@vocabularies")

        self.assertEqual(response.status_code, 200)

        api_session.close()

    def test_anonymous_can_get_allowed_vocabularies(self):
        api_session = RelativeSession(self.portal_url)
        api_session.headers.update({"Accept": "application/json"})
        response = api_session.get("/@vocabularies/plone.app.vocabularies.Keywords")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["items_total"], 2)
        self.assertEqual(response.json()["items"][0]["title"], "bar")
        self.assertEqual(response.json()["items"][1]["title"], "foo")

        api_session.close()

    def test_authenticated_can_get_allowed_vocabularies(self):
        api_session = RelativeSession(self.portal_url)
        api_session.headers.update({"Accept": "application/json"})

        for username in ["member", "contributor", "editor"]:
            api_session.auth = (username, "secret")
            response = api_session.get("/@vocabularies/plone.app.vocabularies.Keywords")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["items_total"], 2)
            self.assertEqual(response.json()["items"][0]["title"], "bar")
            self.assertEqual(response.json()["items"][1]["title"], "foo")

        api_session.close()

    def test_anonymous_cant_get_other_vocabularies(self):
        api_session = RelativeSession(self.portal_url)
        api_session.headers.update({"Accept": "application/json"})
        response = api_session.get("/@vocabularies/plone.app.vocabularies.Users")

        self.assertEqual(response.status_code, 401)

        api_session.close()

    def test_users_cant_get_other_vocabularies(self):
        api_session = RelativeSession(self.portal_url)
        api_session.headers.update({"Accept": "application/json"})

        api_session.auth = ("member", "secret")
        response = api_session.get("/@vocabularies/plone.app.vocabularies.Users")

        self.assertEqual(response.status_code, 403)

        api_session.close()
