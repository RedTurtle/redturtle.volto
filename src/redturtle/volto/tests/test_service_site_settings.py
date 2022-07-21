# -*- coding: utf-8 -*-
import unittest

import transaction
from plone import api
from plone.app.testing import (
    SITE_OWNER_NAME,
    SITE_OWNER_PASSWORD,
    TEST_USER_ID,
    setRoles,
)
from plone.restapi.testing import RelativeSession
from redturtle.volto.testing import REDTURTLE_VOLTO_API_FUNCTIONAL_TESTING
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.interfaces import ISiteSchema
from zope.component import getUtility

SITE_LOGO_BASE64 = (
    b"filenameb64:cGl4ZWwucG5n;datab64:iVBORw0KGgoAAAANSUhEUgA"
    b"AAAEAAAABCAIAAACQd1PeAAAADElEQVQI12P4z8AAAAMBAQAY3Y2wAAA"
    b"AAElFTkSuQmCC"
)

ALTERNATIVE_SITE_LOGO_BASE64 = (
    b"filenameb64:cmVkdHVydGxlLnBuZw==;datab64:iVBORw0KGgoAAAANSUhEUgA"
    b"AAAEAAAABCAIAAACQd1PeAAAADElEQVQI12P4z8AAAAMBAQAY3Y2wAAA"
    b"AAElFTkSuQmCC"
)


class TestServicesSiteSettings(unittest.TestCase):

    layer = REDTURTLE_VOLTO_API_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

        self.api_session_anon = RelativeSession(self.portal_url)
        self.api_session_anon.headers.update({"Accept": "application/json"})

        self.folder = api.content.create(
            container=self.portal,
            type="Folder",
            title="Folder",
            description="",
        )

        transaction.commit()

    def tearDown(self):
        self.api_session.close()
        self.api_session_anon.close()

    def update_registry(self, field, value):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ISiteSchema, prefix="plone")
        setattr(settings, field, value)
        transaction.commit()

    def test_route_exists(self):
        response = self.api_session.get("@site-settings")
        self.assertEqual(response.status_code, 200)

    def test_route_can_be_called_only_on_root(self):
        response = self.api_session.get("/folder/@site-settings")
        self.assertEqual(response.status_code, 404)

    def test_anon_can_see_route(self):
        response = self.api_session_anon.get("@site-settings")
        self.assertEqual(response.status_code, 200)

    def test_return_site_title(self):
        response = self.api_session.get("/@site-settings")
        data = response.json()

        self.assertEqual(data["site_title"], "Plone site")

        self.update_registry("site_title", "Foo")
        response = self.api_session.get("/@site-settings")
        data = response.json()

        self.assertEqual(data["site_title"], "Foo")

    def test_return_default_logo_if_not_set(self):
        response = self.api_session.get("/@site-settings")
        data = response.json()

        self.assertEqual(
            data["site_logo"]["download"], "{}/logo.png".format(self.portal_url)
        )
        self.assertEqual(data["site_logo"]["filename"], "logo.png")
        self.assertNotIn("scales", data["site_logo"])

    def test_return_logo_set_in_registry(self):

        self.update_registry(field="site_logo", value=SITE_LOGO_BASE64)

        response = self.api_session.get("/@site-settings")
        data = response.json()

        self.assertEqual(
            data["site_logo"]["download"],
            "{}/@@site-logo/pixel.png".format(self.portal_url),
        )
        self.assertEqual(data["site_logo"]["filename"], "pixel.png")
        self.assertIn("scales", data["site_logo"])

    def test_update_logo_scales_when_update_logo(self):

        self.update_registry(field="site_logo", value=SITE_LOGO_BASE64)

        response = self.api_session.get("/@site-settings")
        data = response.json()

        old_filename = data["site_logo"]["filename"]
        old_scales = data["site_logo"]["scales"]

        self.update_registry(field="site_logo", value=ALTERNATIVE_SITE_LOGO_BASE64)
        response = self.api_session.get("/@site-settings")
        data = response.json()

        new_filename = data["site_logo"]["filename"]
        new_scales = data["site_logo"]["scales"]

        self.assertEqual(old_filename, "pixel.png")
        self.assertEqual(new_filename, "redturtle.png")

        self.assertNotEqual(
            old_scales["thumb"]["download"], new_scales["thumb"]["download"]
        )
