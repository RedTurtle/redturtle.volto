# -*- coding: utf-8 -*-
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from redturtle.volto.testing import REDTURTLE_VOLTO_FUNCTIONAL_TESTING
from transaction import commit


import unittest


class TestBlocksSearchable(unittest.TestCase):

    layer = REDTURTLE_VOLTO_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.document = api.content.create(
            container=self.portal, type="Document", title="Page"
        )

        commit()

    def test_accordion_block_indexed(self):

        self.assertEqual(len(api.content.find(SearchableText="textcordion")), 0)

        self.document.blocks = {
            "xyz": {
                "@type": "accordion",
                "subblocks": [
                    {
                        "id": "123",
                        "text": {"blocks": [{"text": "textcordion"}]},
                        "title": {"blocks": [{"text": "titlecordion"}]},
                    },
                    {
                        "text": {"blocks": [{"text": "textcordion2"}]},
                        "title": {"blocks": [{"text": "titlecordion2"}]},
                    },
                ],
            },
        }
        self.document.blocks_layout = {"items": ["xyz"]}
        self.document.reindexObject()
        commit()

        for x in ["textcordion", "titlecordion", "textcordion2", "titlecordion2"]:
            self.assertEqual(len(api.content.find(SearchableText=x)), 1)
            self.assertEqual(
                api.content.find(SearchableText=x)[0].UID, self.document.UID()
            )

    def test_alert_block_indexed(self):

        self.assertEqual(len(api.content.find(SearchableText="alert")), 0)

        self.document.blocks = {
            "xyz": {"@type": "alert", "text": {"blocks": [{"text": "alert"}]}},
        }
        self.document.blocks_layout = {"items": ["xyz"]}
        self.document.reindexObject()
        commit()

        self.assertEqual(len(api.content.find(SearchableText="alert")), 1)
        self.assertEqual(
            api.content.find(SearchableText="alert")[0].UID, self.document.UID()
        )

    def test_simple_card_block_indexed(self):

        self.assertEqual(len(api.content.find(SearchableText="simpletitle")), 0)

        self.document.blocks = {
            "xyz": {
                "@type": "testo_riquadro_semplice",
                "simple_card_title": {"blocks": [{"text": "simpletitle"}]},
                "simple_card_content": {"blocks": [{"text": "simpletext"}]},
            },
        }
        self.document.blocks_layout = {"items": ["xyz"]}
        self.document.reindexObject()
        commit()

        self.assertEqual(len(api.content.find(SearchableText="simpletitle")), 1)
        self.assertEqual(
            api.content.find(SearchableText="simpletitle")[0].UID, self.document.UID()
        )

        self.assertEqual(len(api.content.find(SearchableText="simpletext")), 1)
        self.assertEqual(
            api.content.find(SearchableText="simpletext")[0].UID, self.document.UID()
        )

    def test_card_with_image_block_indexed(self):

        self.assertEqual(len(api.content.find(SearchableText="imagetitle")), 0)

        self.document.blocks = {
            "xyz": {
                "@type": "testo_riquadro_immagine",
                "image_card_title": {"blocks": [{"text": "imagetitle"}]},
                "image_card_content": {"blocks": [{"text": "imagetext"}]},
            },
        }
        self.document.blocks_layout = {"items": ["xyz"]}
        self.document.reindexObject()
        commit()

        self.assertEqual(len(api.content.find(SearchableText="imagetitle")), 1)
        self.assertEqual(
            api.content.find(SearchableText="imagetitle")[0].UID, self.document.UID()
        )

        self.assertEqual(len(api.content.find(SearchableText="imagetext")), 1)
        self.assertEqual(
            api.content.find(SearchableText="imagetext")[0].UID, self.document.UID()
        )
