# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from redturtle.volto.adapters.rss import CustomFeedItem
from redturtle.volto.interfaces import ICustomFeedItem


try:
    from plone.base.interfaces.syndication import IFeed
except ModuleNotFoundError:
    from Products.CMFPlone.interfaces.syndication import IFeed

from plone.namedfile.file import NamedBlobImage
from redturtle.volto.testing import REDTURTLE_VOLTO_API_FUNCTIONAL_TESTING

import os
import unittest


class TestCustomRSSFeed(unittest.TestCase):
    layer = REDTURTLE_VOLTO_API_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        old_behavior = self.portal["portal_types"]["News Item"].behaviors
        self.portal["portal_types"]["News Item"].behaviors = old_behavior + (
            "volto.preview_image",
        )
        self.portal_url = self.portal.absolute_url()
        self.feed = IFeed(self.portal)
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        filename = os.path.join(os.path.dirname(__file__), "logo.png")
        self.news1 = api.content.create(
            container=self.portal,
            type="News Item",
            title="News 1",
            description="",
        )
        self.news1.image = NamedBlobImage(
            data=open(filename, "rb").read(),
            filename="logo.png",
            contentType="image/png",
        )

        self.news2 = api.content.create(
            container=self.portal,
            type="News Item",
            title="News 2",
            description="",
        )
        self.news2.preview_image = NamedBlobImage(
            data=open(filename, "rb").read(),
            filename="logo.png",
            contentType="image/png",
        )

        self.news3 = api.content.create(
            container=self.portal,
            type="News Item",
            title="News 3",
            description="",
        )
        self.news3.image = NamedBlobImage(
            data=open(filename, "rb").read(),
            filename="image.png",
            contentType="image/png",
        )
        self.news3.preview_image = NamedBlobImage(
            data=open(filename, "rb").read(),
            filename="preview.png",
            contentType="image/png",
        )

    def test_assert_news_has_volto_preview_image(self):
        self.assertTrue(
            "volto.preview_image" in self.portal["portal_types"]["News Item"].behaviors
        )

    def test_rss_item_iface_provided(self):
        self.assertTrue(ICustomFeedItem.providedBy(self.news1))
        self.assertTrue(ICustomFeedItem.providedBy(self.news2))

    def test_rss_item_field_name_image(self):

        adapter_news_1 = CustomFeedItem(self.news1, self.feed)
        adapter_news_2 = CustomFeedItem(self.news2, self.feed)

        # news 1 has image feld
        self.assertEqual(adapter_news_1.field_name, "image")

        # news 2 has the preview image field compiled, so has the default options
        # is to use image field field_name will be None
        self.assertEqual(adapter_news_2.field_name, None)

    def test_rss_item_field_name_preview_image(self):

        api.portal.set_registry_record(
            "redturtle.volto.rss_image_choice", "preview_image"
        )
        adapter_news_1 = CustomFeedItem(self.news1, self.feed)
        adapter_news_2 = CustomFeedItem(self.news2, self.feed)

        self.assertEqual(adapter_news_1.field_name, None)
        self.assertEqual(adapter_news_2.field_name, "preview_image")

    def test_rss_item_field_name_like_listing(self):
        api.portal.set_registry_record(
            "redturtle.volto.rss_image_choice", "listing_like"
        )
        adapter_news_1 = CustomFeedItem(self.news1, self.feed)
        adapter_news_2 = CustomFeedItem(self.news2, self.feed)
        adapter_news_3 = CustomFeedItem(self.news3, self.feed)

        self.assertEqual(adapter_news_1.field_name, "image")
        self.assertEqual(adapter_news_2.field_name, "preview_image")
        # image 3 has both image and preview_image, so the preview one is used
        self.assertEqual(adapter_news_3.field_name, "preview_image")
