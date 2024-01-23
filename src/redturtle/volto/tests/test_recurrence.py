import unittest
from unittest import mock
from unittest.mock import Mock

import pytz
import transaction
import zope.component
from datetime import datetime, timedelta
from OFS.SimpleItem import SimpleItem
from plone.app.event.base import RET_MODE_ACCESSORS
from plone.app.event.base import get_events
from plone.app.event.dx.traverser import OccurrenceTraverser
from plone.app.event.recurrence import Occurrence
from plone.app.event.testing import PAEvent_INTEGRATION_TESTING
from plone.app.event.testing import PAEventDX_FUNCTIONAL_TESTING
from plone.app.event.testing import PAEventDX_INTEGRATION_TESTING
from plone.app.event.testing import set_browserlayer
from plone.app.event.testing import set_env_timezone
from plone.app.event.testing import set_timezone
from plone.app.event.tests.base_setup import AbstractSampleDataEvents
from plone.app.event.tests.base_setup import patched_now
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_PASSWORD
from plone.app.testing import setRoles
from plone.dexterity.utils import createContentInContainer
from plone.event.interfaces import IEvent
from plone.event.interfaces import IEventAccessor
from plone.event.interfaces import IEventRecurrence
from plone.event.interfaces import IOccurrence
from plone.event.interfaces import IRecurrenceSupport
from plone.testing.zope import Browser
from zope.annotation.interfaces import IAnnotations
from zope.interface import alsoProvides
from zope.publisher.interfaces.browser import IBrowserView

from redturtle.volto.testing import REDTURTLE_VOLTO_FUNCTIONAL_TESTING

TZNAME = "Europe/Rome"


class TestOccurrences(unittest.TestCase):
    layer = REDTURTLE_VOLTO_FUNCTIONAL_TESTING

    def setUp(self):

        self.portal = self.layer["portal"]
        self.request = self.layer["request"]

        set_browserlayer(self.request)
        set_env_timezone(TZNAME)
        set_timezone(TZNAME)

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

        start_date_search = datetime.strptime("02/01/2024 10:00:00", "%d/%m/%Y %H:%M:%S")
        end_date_search = start_date_search + timedelta(hours=1)

        results = catalog(
            end={"query": (start_date_search, end_date_search), "range": "min:max"}
        )

        self.assertFalse(results)
