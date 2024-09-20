# -*- coding: utf-8 -*-
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from redturtle.volto.testing import REDTURTLE_VOLTO_INTEGRATION_TESTING

import unittest


class TestFindBrokenLinksView(unittest.TestCase):
    layer = REDTURTLE_VOLTO_INTEGRATION_TESTING
    maxDiff = None

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.view = api.content.get_view(
            name="find-broken-links", context=self.portal, request=self.request
        )

    def test_view_does_not_return_contents_if_have_working_links(self):
        page_a = api.content.create(
            container=self.portal, type="Document", title="Page A"
        )

        api.content.create(
            container=self.portal,
            type="Document",
            title="Page B",
            blocks={"xxx": {"foo": f"resolveuid/{page_a.UID()}"}},
        )

        self.assertEqual([], self.view.check_links())

    def test_view_return_contents_with_broken_links(self):
        page_a = api.content.create(
            container=self.portal, type="Document", title="Page A"
        )

        page_b = api.content.create(
            container=self.portal,
            type="Document",
            title="Page B",
            blocks={"xxx": {"foo": f"resolveuid/{page_a.UID()}"}},
        )
        api.content.delete(obj=page_a, check_linkintegrity=False)

        res = self.view.check_links()
        self.assertEqual(len(res), 1)
        self.assertIn(page_b.absolute_url(), res)

    def test_view_can_check_several_patterns(self):
        page_a = api.content.create(
            container=self.portal, type="Document", title="Page A"
        )

        page_b = api.content.create(
            container=self.portal,
            type="Document",
            title="Page B",
            blocks={"xxx": {"bar": f"../resolveuid/{page_a.UID()}"}},
        )

        page_c = api.content.create(
            container=self.portal,
            type="Document",
            title="Page C",
            blocks={"xxx": {"baz": f"../resolveuid/{page_a.UID()}/asd"}},
        )
        api.content.delete(obj=page_a, check_linkintegrity=False)

        res = self.view.check_links()
        self.assertEqual(len(res), 2)
        self.assertIn(page_b.absolute_url(), res)
        self.assertIn(page_c.absolute_url(), res)
