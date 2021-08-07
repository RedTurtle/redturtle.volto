# -*- coding: utf-8 -*-
from plone.app.testing import (
    SITE_OWNER_NAME,
    SITE_OWNER_PASSWORD,
    TEST_USER_ID,
    setRoles,
)
from plone.restapi.testing import RelativeSession
from redturtle.volto.testing import REDTURTLE_VOLTO_API_FUNCTIONAL_TESTING
from DateTime import DateTime
from transaction import commit
from plone.registry.interfaces import IRegistry
from zope.component import getUtility

import unittest
import time
import os


class TestPublicationFieldsFixes(unittest.TestCase):

    layer = REDTURTLE_VOLTO_API_FUNCTIONAL_TESTING

    def setUp(self):
        tz = "Europe/Rome"
        os.environ["TZ"] = tz
        time.tzset()

        # Patch DateTime's timezone for deterministic behavior.
        self.DT_orig_localZone = DateTime.localZone
        DateTime.localZone = lambda cls=None, ltm=None: tz

        from plone.dexterity import content

        content.FLOOR_DATE = DateTime(1970, 0)
        content.CEILING_DATE = DateTime(2500, 0)
        self._orig_content_zone = content._zone
        content._zone = "GMT+2"

        reg_key = "plone.portal_timezone"
        registry = getUtility(IRegistry)
        registry[reg_key] = tz

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

        if "TZ" in os.environ:
            del os.environ["TZ"]
        time.tzset()

        from DateTime import DateTime

        DateTime.localZone = self.DT_orig_localZone

        from plone.dexterity import content

        content._zone = self._orig_content_zone
        content.FLOOR_DATE = DateTime(1970, 0)
        content.CEILING_DATE = DateTime(2500, 0)

        reg_key = "plone.portal_timezone"
        registry = getUtility(IRegistry)
        registry[reg_key] = "UTC"

    # def test_set_effective_date_store_right_value_in_plone(self):
    #     now = DateTime()
    #     # now_localized = now_utc.astimezone(self.t_zone)
    #     response = self.api_session.post(
    #         self.portal_url,
    #         json={
    #             "@type": "Document",
    #             "id": "mydocument",
    #             "title": "My Document",
    #             "effective": "{}Z".format(now.utcdatetime().isoformat()),
    #         },
    #     )
    #     commit()
    #     # self.assertEqual(201, response.status_code)