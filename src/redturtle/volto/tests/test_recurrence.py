from datetime import datetime
from datetime import timedelta
from plone.app.event.testing import set_browserlayer
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.dexterity.utils import createContentInContainer
from redturtle.volto.testing import REDTURTLE_VOLTO_FUNCTIONAL_TESTING

import unittest


class TestOccurrences(unittest.TestCase):
    layer = REDTURTLE_VOLTO_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        set_browserlayer(self.request)
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.start_date = datetime.strptime("01/01/2024 10:00:00", "%d/%m/%Y %H:%M:%S")
        self.end_date = self.start_date + timedelta(hours=1)

        self.event = createContentInContainer(
            self.portal,
            "Event",
            id="test-event",
            title="Test Event",
            start=self.start_date,
            end=self.end_date,
            location="Vienna",
            recurrence="RRULE:FREQ=WEEKLY;INTERVAL=1;BYDAY=MO;COUNT=50",
        )

    def test_get_occurrences_from_catalog(self):
        catalog = self.portal.portal_catalog

        start_date_search = datetime.strptime(
            "02/01/2024 10:00:00", "%d/%m/%Y %H:%M:%S"
        )
        end_date_search = start_date_search + timedelta(hours=1)

        results = catalog(
            end={"query": (start_date_search, end_date_search), "range": "min:max"}
        )

        self.assertFalse(results)
