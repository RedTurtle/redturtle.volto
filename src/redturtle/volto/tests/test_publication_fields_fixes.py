# -*- coding: utf-8 -*-
from datetime import timedelta
from plone.app.event.base import localized_now
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.testing import RelativeSession
from redturtle.volto.testing import REDTURTLE_VOLTO_API_FUNCTIONAL_TESTING
from transaction import commit

import unittest


class TestPublicationFieldsFixes(unittest.TestCase):
    layer = REDTURTLE_VOLTO_API_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

    def tearDown(self):
        self.api_session.close()

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
