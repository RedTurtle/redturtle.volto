# -*- coding: utf-8 -*-
from plone import api
from plone.app.contenttypes.behaviors.collection import (
    ICollection as ICollection_behavior,
)
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.namedfile.file import NamedBlobImage
from plone.restapi.testing import RelativeSession
from redturtle.volto.testing import REDTURTLE_VOLTO_API_FUNCTIONAL_TESTING

import os
import transaction
import unittest


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

        filename = os.path.join(os.path.dirname(__file__), "logo.png")
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
        response = self.api_session.get("/@search", params={"portal_type": "News Item"})
        self.assertEqual(response.status_code, 200)
        res = response.json()

        self.assertEqual(len(res["items"]), 2)
        self.assertEqual(res["items"][0]["title"], self.news_with_image.title)
        self.assertEqual(res["items"][1]["title"], self.news_without_image.title)
        self.assertNotIn("image", res["items"][0])
        self.assertNotIn("image", res["items"][1])

    def test_summary_return_image_scales_if_requested(self):
        response = self.api_session.get(
            "/@search?metadata_fields=_all", params={"portal_type": "News Item"}
        )
        self.assertEqual(response.status_code, 200)
        res = response.json()

        self.assertEqual(len(res["items"]), 2)
        self.assertEqual(res["items"][0]["title"], self.news_with_image.title)
        self.assertEqual(res["items"][1]["title"], self.news_without_image.title)
        self.assertIn("image", res["items"][0])
        self.assertNotIn("image", res["items"][1])

    def test_summary_return_empty_effective_date_if_not_set(self):
        page = api.content.create(
            container=self.portal,
            type="Document",
            title="Document",
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

    def test_summary_serializer_with_links_in_collection_results(self):
        link = api.content.create(
            container=self.portal,
            type="Link",
            title="Funny link",
        )
        link.remoteUrl = "/events"
        # allow to add collection
        portal = api.portal.get()
        pt = portal.portal_types
        pt["Collection"].global_allow = True
        # add a collection to find links
        collection = api.content.create(
            container=self.portal,
            type="Collection",
            title="A collection",
        )
        wrapped = ICollection_behavior(collection)
        wrapped.query = [
            {
                "i": "portal_type",
                "o": "plone.app.querystring.operation.string.is",
                "v": "Link",
            },
        ]
        transaction.commit()
        # Check if only the item inside folder1 is returned, since it's a
        # navigation root.
        response = self.api_session.get(collection.getId())
        items = response.json().get("items", [])
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["title"], "Funny link")
