# -*- coding: utf-8 -*-
from plone import api
from plone.app.testing import (
    SITE_OWNER_NAME,
    SITE_OWNER_PASSWORD,
    TEST_USER_ID,
    setRoles,
)
from plone.restapi.testing import RelativeSession
from plone.namedfile.file import NamedBlobImage
from redturtle.volto.testing import REDTURTLE_VOLTO_API_FUNCTIONAL_TESTING
from datetime import datetime
import unittest
import transaction
import os


class TestSummaryCustomization(unittest.TestCase):

    layer = REDTURTLE_VOLTO_API_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

        self.news_with_image = api.content.create(
            container=self.portal,
            type="News Item",
            title="News with image",
            description="",
        )

        self.news_without_image = api.content.create(
            container=self.portal,
            type="News Item",
            title="News without image",
            description="",
        )

        filename = os.path.join(os.path.dirname(__file__), u"logo.png")
        self.news_with_image.image = NamedBlobImage(
            data=open(filename, "rb").read(),
            filename="logo.png",
            contentType="image/png",
        )

        self.news_with_image.reindexObject()

        transaction.commit()

    def tearDown(self):
        self.api_session.close()

    def test_summary_does_not_return_image_scales_if_not_requested(self):
        response = self.api_session.get("/@search")
        self.assertEqual(response.status_code, 200)
        res = response.json()

        self.assertEqual(len(res["items"]), 2)
        self.assertEqual(res["items"][0]["title"], self.news_with_image.title)
        self.assertEqual(
            res["items"][1]["title"], self.news_without_image.title
        )
        self.assertNotIn("image", res["items"][0])
        self.assertNotIn("image", res["items"][1])

    def test_summary_return_image_scales_if_requested(self):
        response = self.api_session.get("/@search?metadata_fields=_all")
        self.assertEqual(response.status_code, 200)
        res = response.json()

        self.assertEqual(len(res["items"]), 2)
        self.assertEqual(res["items"][0]["title"], self.news_with_image.title)
        self.assertEqual(
            res["items"][1]["title"], self.news_without_image.title
        )
        self.assertIn("image", res["items"][0])
        self.assertNotIn("image", res["items"][1])

    def test_summary_return_empty_effective_date_if_not_set(self):
        page = api.content.create(
            container=self.portal, type="Document", title="Document",
        )
        transaction.commit()

        response = self.api_session.get(
            "/@search?metadata_fields=effective&UID={}".format(page.UID())
        )
        self.assertEqual(response.status_code, 200)
        res = response.json()

        self.assertEqual(len(res["items"]), 1)
        self.assertEqual(res["items"][0]["effective"], None)

        api.content.transition(obj=page, transition="publish")
        transaction.commit()

        res = self.api_session.get(
            "/@search?metadata_fields=effective&UID={}".format(page.UID())
        ).json()

        self.assertEqual(len(res["items"]), 1)
        self.assertEqual(res["items"][0]["effective"], page.effective_date)

    def test_event_summary_on_recurrence(self):
        event = api.content.create(
            container=self.portal, type="Event", title="Event with recurrence",
        )
        event.start = datetime(2022, 1, 9, 13, 0)
        event.end = datetime(2022, 4, 24, 14, 0)
        event.recurrence = "DTSTART:20220109T000000Z\nRRULE:FREQ=WEEKLY;INTERVAL=1;UNTIL=20220424T000000Z;BYDAY=SU,SA"  # noqa
        event.reindexObject()
        transaction.commit()
        res = self.api_session.post(
            self.portal_url + "/@querystring-search",
            json={
                "metadata_fields": "_all",
                "b_size": 24,
                "query": [
                    {
                        "i": "portal_type",
                        "o": "plone.app.querystring.operation.selection.any",
                        "v": ["Event"],
                    },
                    {
                        "i": "start",
                        "o": "plone.app.querystring.operation.date.afterToday",
                        "v": "",
                    },
                ],
                "sort_on": "start",
                "sort_order": "ascending",
                "b_start": 0,
            },
        )
        item = res.json()["items"]
        self.assertEqual(len(item), 0)
