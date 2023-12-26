# -*- coding: utf-8 -*-
from DateTime import DateTime
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.registry.interfaces import IRegistry
from plone.restapi.testing import RelativeSession
from redturtle.volto.testing import REDTURTLE_VOLTO_API_FUNCTIONAL_TESTING
from transaction import commit
from zope.component import getUtility

import os
import unittest


class TestPublicationFieldsFixes(unittest.TestCase):
    layer = REDTURTLE_VOLTO_API_FUNCTIONAL_TESTING

    def setUp(self):
        tz = os.environ.get("TZ", "UTC")

        registry = getUtility(IRegistry)
        self._orig_tz = (
            registry["plone.portal_timezone"],
            registry["plone.available_timezones"],
        )
        registry["plone.portal_timezone"] = tz
        registry["plone.available_timezones"] = [tz]
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

        commit()

    def tearDown(self):
        self.api_session.close()
        registry = getUtility(IRegistry)
        registry["plone.portal_timezone"] = self._orig_tz[0]
        registry["plone.available_timezones"] = self._orig_tz[1]

    def test_set_effective_date_store_right_value_in_plone(self):
        effective = DateTime()
        expires = effective + 1
        self.api_session.post(
            self.portal_url,
            json={
                "@type": "Document",
                "id": "mydocument",
                "title": "My Document",
                "effective": "{}Z".format(effective.utcdatetime().isoformat()),
                "expires": "{}Z".format(expires.utcdatetime().isoformat()),
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
