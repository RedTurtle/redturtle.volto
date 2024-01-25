# -*- coding: utf-8 -*-
import os
import unittest
from datetime import timedelta

from plone.app.event.base import localized_now
from plone.app.event.testing import set_env_timezone
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.registry.interfaces import IRegistry
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.testing import RelativeSession
from transaction import commit
from zope.component import getUtility

from redturtle.volto.testing import REDTURTLE_VOLTO_API_FUNCTIONAL_TESTING


class TestPublicationFieldsFixes(unittest.TestCase):
    layer = REDTURTLE_VOLTO_API_FUNCTIONAL_TESTING

    def setUp(self):
        self.orig_env_tz = os.environ.get("TZ", None)
        tz = "Europe/Rome"
        set_env_timezone(tz)
        registry = getUtility(IRegistry)
        self._orig_tz = (
            registry["plone.portal_timezone"],
            registry["plone.available_timezones"],
        )
        registry["plone.portal_timezone"] = tz
        registry["plone.available_timezones"] = [tz]
        commit()

        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

    def tearDown(self):
        self.api_session.close()
        registry = getUtility(IRegistry)
        registry["plone.portal_timezone"] = self._orig_tz[0]
        registry["plone.available_timezones"] = self._orig_tz[1]
        set_env_timezone(self.orig_env_tz)

    def test_set_effective_date_store_right_value_in_plone(self):
        effective = localized_now()
        expires = effective + timedelta(days=1)
        self.api_session.post(
            self.portal_url,
            json={
                "@type": "Document",
                "id": "mydocument",
                "title": "My Document",
                "effective": f"{json_compatible(effective)}",
                "expires": f"{json_compatible(expires)}",
            },
        )
        commit()
        self.assertEqual(
            self.portal["mydocument"].effective().strftime("%d-%m-%Y %H:%M"),
            effective.strftime("%d-%m-%Y %H:%M"),
        )
        self.assertEqual(
            self.portal["mydocument"].expires().strftime("%d-%m-%Y %H:%M"),
            expires.strftime("%d-%m-%Y %H:%M"),
        )
