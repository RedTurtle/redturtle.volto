# -*- coding: utf-8 -*-
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.namedfile.file import NamedBlobImage
from plone.restapi.testing import RelativeSession
from redturtle.volto.testing import REDTURTLE_VOLTO_API_FUNCTIONAL_TESTING
from transaction import commit

import os
import unittest


class PloneSiteSEOTest(unittest.TestCase):
    layer = REDTURTLE_VOLTO_API_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        self.portal_url = self.portal.absolute_url()

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

        setRoles(self.portal, TEST_USER_ID, ["Manager"])

    def test_behavior_enabled(self):
        portal_types = api.portal.get_tool(name="portal_types")
        self.assertIn("kitconcept.seo", portal_types["Plone Site"].behaviors)

    def test_can_access_image_scales_on_plone_site(self):
        filename = os.path.join(os.path.dirname(__file__), "logo.png")

        self.portal.opengraph_image = NamedBlobImage(
            data=open(filename, "rb").read(),
            filename="logo.png",
            contentType="image/png",
        )
        commit()
        scales = api.content.get_view(
            name="images", context=self.portal, request=self.request
        )
        self.assertEqual(scales.scale("opengraph_image").width, 441)
        self.assertEqual(scales.scale("opengraph_image").height, 114)

        api_res = self.api_session.get("").json()
        self.assertIn("scales", api_res["opengraph_image"])
        self.assertEqual(api_res["opengraph_image"]["width"], 441)
        self.assertEqual(api_res["opengraph_image"]["height"], 114)
