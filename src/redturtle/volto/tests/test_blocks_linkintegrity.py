# -*- coding: utf-8 -*-
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from redturtle.volto.testing import REDTURTLE_VOLTO_FUNCTIONAL_TESTING
from transaction import commit
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent

import unittest


class TestBlocksLinkIntegrity(unittest.TestCase):
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

        self.ref = api.content.create(
            container=self.portal, type="Document", title="Reference Page"
        )

        commit()

    def get_references(self):
        links_info = self.ref.restrictedTraverse("@@delete_confirmation_info")
        return links_info.get_breaches()

    def test_testo_riquadro_semplice_link_integrity(self):
        self.assertEqual(self.get_references(), [])
        self.document.blocks = {
            "xyz": {
                "@type": "testo_riquadro_semplice",
                "simple_card_content": [
                    {
                        "type": "p",
                        "children": [
                            {
                                "type": "link",
                                "data": {
                                    "url": f"/resolveuid/{self.ref.UID()}",
                                },
                                "children": [{"text": "foo"}],
                            },
                        ],
                    }
                ],
            }
        }
        notify(ObjectModifiedEvent(self.document))

        references = self.get_references()
        reference = references[0]

        self.assertEqual(len(references), 1)
        self.assertEqual(len(reference["sources"]), 1)
        self.assertEqual(reference["sources"][0]["uid"], self.document.UID())
        self.assertEqual(reference["target"]["uid"], self.ref.UID())

    def test_alert_link_integrity(self):
        self.assertEqual(self.get_references(), [])
        self.document.blocks = {
            "xyz": {
                "@type": "alert",
                "text": [
                    {
                        "type": "p",
                        "children": [
                            {
                                "type": "link",
                                "data": {
                                    "url": f"/resolveuid/{self.ref.UID()}",
                                },
                                "children": [{"text": "foo"}],
                            },
                        ],
                    }
                ],
            }
        }
        notify(ObjectModifiedEvent(self.document))

        references = self.get_references()
        reference = references[0]

        self.assertEqual(len(references), 1)
        self.assertEqual(len(reference["sources"]), 1)
        self.assertEqual(reference["sources"][0]["uid"], self.document.UID())
        self.assertEqual(reference["target"]["uid"], self.ref.UID())

    def test_accordion_description_link_integrity(self):
        self.assertEqual(self.get_references(), [])
        self.document.blocks = {
            "xyz": {
                "@type": "accordion",
                "description": [
                    {
                        "type": "p",
                        "children": [
                            {
                                "type": "link",
                                "data": {
                                    "url": f"/resolveuid/{self.ref.UID()}",
                                },
                                "children": [{"text": "foo"}],
                            },
                        ],
                    }
                ],
            }
        }
        notify(ObjectModifiedEvent(self.document))

        references = self.get_references()
        reference = references[0]

        self.assertEqual(len(references), 1)
        self.assertEqual(len(reference["sources"]), 1)
        self.assertEqual(reference["sources"][0]["uid"], self.document.UID())
        self.assertEqual(reference["target"]["uid"], self.ref.UID())

    def test_accordion_subblocks_link_integrity(self):
        self.assertEqual(self.get_references(), [])
        self.document.blocks = {
            "xyz": {
                "@type": "accordion",
                "subblocks": [
                    {
                        "id": "1730818016757",
                        "title": "title",
                        "text": [
                            {
                                "type": "p",
                                "children": [
                                    {
                                        "type": "link",
                                        "data": {
                                            "url": f"/resolveuid/{self.ref.UID()}",
                                        },
                                        "children": [{"text": "foo"}],
                                    },
                                ],
                            }
                        ],
                    }
                ],
            }
        }
        notify(ObjectModifiedEvent(self.document))

        references = self.get_references()
        reference = references[0]

        self.assertEqual(len(references), 1)
        self.assertEqual(len(reference["sources"]), 1)
        self.assertEqual(reference["sources"][0]["uid"], self.document.UID())
        self.assertEqual(reference["target"]["uid"], self.ref.UID())

    def test_testo_riquadro_immagine_link_integrity(self):
        self.assertEqual(self.get_references(), [])
        self.document.blocks = {
            "xyz": {
                "@type": "testo_riquadro_immagine",
                "image_card_content": [
                    {
                        "type": "p",
                        "children": [
                            {
                                "type": "link",
                                "data": {
                                    "url": f"/resolveuid/{self.ref.UID()}",
                                },
                                "children": [{"text": "foo"}],
                            },
                        ],
                    }
                ],
            }
        }
        notify(ObjectModifiedEvent(self.document))

        references = self.get_references()
        reference = references[0]

        self.assertEqual(len(references), 1)
        self.assertEqual(len(reference["sources"]), 1)
        self.assertEqual(reference["sources"][0]["uid"], self.document.UID())
        self.assertEqual(reference["target"]["uid"], self.ref.UID())

    def test_callout_block_link_integrity(self):
        self.assertEqual(self.get_references(), [])
        self.document.blocks = {
            "xyz": {
                "@type": "callout_block",
                "text": [
                    {
                        "type": "p",
                        "children": [
                            {
                                "type": "link",
                                "data": {
                                    "url": f"/resolveuid/{self.ref.UID()}",
                                },
                                "children": [{"text": "foo"}],
                            },
                        ],
                    }
                ],
            }
        }
        notify(ObjectModifiedEvent(self.document))

        references = self.get_references()
        reference = references[0]

        self.assertEqual(len(references), 1)
        self.assertEqual(len(reference["sources"]), 1)
        self.assertEqual(reference["sources"][0]["uid"], self.document.UID())
        self.assertEqual(reference["target"]["uid"], self.ref.UID())

    def test_cta_block_link_integrity(self):
        self.assertEqual(self.get_references(), [])
        self.document.blocks = {
            "xyz": {
                "@type": "cta_block",
                "cta_content": [
                    {
                        "type": "p",
                        "children": [
                            {
                                "type": "link",
                                "data": {
                                    "url": f"/resolveuid/{self.ref.UID()}",
                                },
                                "children": [{"text": "foo"}],
                            },
                        ],
                    }
                ],
            }
        }
        notify(ObjectModifiedEvent(self.document))

        references = self.get_references()
        reference = references[0]

        self.assertEqual(len(references), 1)
        self.assertEqual(len(reference["sources"]), 1)
        self.assertEqual(reference["sources"][0]["uid"], self.document.UID())
        self.assertEqual(reference["target"]["uid"], self.ref.UID())

    def test_cta_block_ctalink_link_integrity(self):
        self.assertEqual(self.get_references(), [])
        self.document.blocks = {
            "xyz": {"@type": "cta_block", "ctaLink": f"/resolveuid/{self.ref.UID()}"}
        }
        notify(ObjectModifiedEvent(self.document))

        references = self.get_references()
        reference = references[0]

        self.assertEqual(len(references), 1)
        self.assertEqual(len(reference["sources"]), 1)
        self.assertEqual(reference["sources"][0]["uid"], self.document.UID())
        self.assertEqual(reference["target"]["uid"], self.ref.UID())

    def test_cta_block_background_link_integrity(self):
        self.assertEqual(self.get_references(), [])
        self.document.blocks = {
            "xyz": {"@type": "cta_block", "ctaImage": [self.ref.UID()]}
        }
        notify(ObjectModifiedEvent(self.document))

        references = self.get_references()
        reference = references[0]

        self.assertEqual(len(references), 1)
        self.assertEqual(len(reference["sources"]), 1)
        self.assertEqual(reference["sources"][0]["uid"], self.document.UID())
        self.assertEqual(reference["target"]["uid"], self.ref.UID())

    def test_table_block_link_integrity(self):
        self.assertEqual(self.get_references(), [])
        self.document.blocks = {
            "xyz": {
                "table": {
                    "rows": [
                        {
                            "key": "1l9ut",
                            "cells": [
                                {
                                    "key": "7j218",
                                    "type": "header",
                                    "value": [
                                        {
                                            "type": "p",
                                            "children": [
                                                {
                                                    "type": "link",
                                                    "data": {
                                                        "url": f"resolveuid/{self.ref.UID()}",
                                                    },
                                                    "children": [{"text": "foo"}],
                                                },
                                            ],
                                        }
                                    ],
                                },
                                {
                                    "key": "cumu9",
                                    "type": "header",
                                    "value": [
                                        {"type": "p", "children": [{"text": "bbb"}]}
                                    ],
                                },
                            ],
                        },
                    ],
                },
                "@type": "slateTable",
            }
        }
        notify(ObjectModifiedEvent(self.document))

        references = self.get_references()
        reference = references[0]

        self.assertEqual(len(references), 1)
        self.assertEqual(len(reference["sources"]), 1)
        self.assertEqual(reference["sources"][0]["uid"], self.document.UID())
        self.assertEqual(reference["target"]["uid"], self.ref.UID())

    def test_contacts_block_description_link_integrity(self):
        self.assertEqual(self.get_references(), [])
        self.document.blocks = {
            "xyz": {
                "@type": "contacts",
                "description": [
                    {
                        "type": "p",
                        "children": [
                            {
                                "type": "link",
                                "data": {
                                    "url": f"/resolveuid/{self.ref.UID()}",
                                },
                                "children": [{"text": "foo"}],
                            },
                        ],
                    }
                ],
            }
        }
        notify(ObjectModifiedEvent(self.document))

        references = self.get_references()
        reference = references[0]

        self.assertEqual(len(references), 1)
        self.assertEqual(len(reference["sources"]), 1)
        self.assertEqual(reference["sources"][0]["uid"], self.document.UID())
        self.assertEqual(reference["target"]["uid"], self.ref.UID())

    def test_contacts_block_subblocks_text_link_integrity(self):
        self.assertEqual(self.get_references(), [])
        self.document.blocks = {
            "xyz": {
                "@type": "contacts",
                "subblocks": [
                    {
                        "text": [
                            {
                                "type": "p",
                                "children": [
                                    {
                                        "type": "link",
                                        "data": {
                                            "url": f"/resolveuid/{self.ref.UID()}",
                                        },
                                        "children": [{"text": "foo"}],
                                    },
                                ],
                            }
                        ]
                    }
                ],
            }
        }
        notify(ObjectModifiedEvent(self.document))

        references = self.get_references()
        reference = references[0]

        self.assertEqual(len(references), 1)
        self.assertEqual(len(reference["sources"]), 1)
        self.assertEqual(reference["sources"][0]["uid"], self.document.UID())
        self.assertEqual(reference["target"]["uid"], self.ref.UID())

    def test_contacts_block_subblocks_tel_link_integrity(self):
        self.assertEqual(self.get_references(), [])
        self.document.blocks = {
            "xyz": {
                "@type": "contacts",
                "subblocks": [
                    {
                        "tel": [
                            {
                                "type": "p",
                                "children": [
                                    {
                                        "type": "link",
                                        "data": {
                                            "url": f"/resolveuid/{self.ref.UID()}",
                                        },
                                        "children": [{"text": "foo"}],
                                    },
                                ],
                            }
                        ]
                    }
                ],
            }
        }
        notify(ObjectModifiedEvent(self.document))

        references = self.get_references()
        reference = references[0]

        self.assertEqual(len(references), 1)
        self.assertEqual(len(reference["sources"]), 1)
        self.assertEqual(reference["sources"][0]["uid"], self.document.UID())
        self.assertEqual(reference["target"]["uid"], self.ref.UID())

    def test_contacts_block_subblocks_email_link_integrity(self):
        self.assertEqual(self.get_references(), [])
        self.document.blocks = {
            "xyz": {
                "@type": "contacts",
                "subblocks": [
                    {
                        "email": [
                            {
                                "type": "p",
                                "children": [
                                    {
                                        "type": "link",
                                        "data": {
                                            "url": f"/resolveuid/{self.ref.UID()}",
                                        },
                                        "children": [{"text": "foo"}],
                                    },
                                ],
                            }
                        ]
                    }
                ],
            }
        }
        notify(ObjectModifiedEvent(self.document))

        references = self.get_references()
        reference = references[0]

        self.assertEqual(len(references), 1)
        self.assertEqual(len(reference["sources"]), 1)
        self.assertEqual(reference["sources"][0]["uid"], self.document.UID())
        self.assertEqual(reference["target"]["uid"], self.ref.UID())

    def test_icon_block_description_link_integrity(self):
        self.assertEqual(self.get_references(), [])
        self.document.blocks = {
            "xyz": {
                "@type": "iconBlocks",
                "description": [
                    {
                        "type": "p",
                        "children": [
                            {
                                "type": "link",
                                "data": {
                                    "url": f"/resolveuid/{self.ref.UID()}",
                                },
                                "children": [{"text": "foo"}],
                            },
                        ],
                    }
                ],
            }
        }
        notify(ObjectModifiedEvent(self.document))

        references = self.get_references()
        reference = references[0]

        self.assertEqual(len(references), 1)
        self.assertEqual(len(reference["sources"]), 1)
        self.assertEqual(reference["sources"][0]["uid"], self.document.UID())
        self.assertEqual(reference["target"]["uid"], self.ref.UID())

    def test_icon_block_href_link_integrity(self):
        self.assertEqual(self.get_references(), [])
        self.document.blocks = {
            "xyz": {"@type": "iconBlocks", "href": f"/resolveuid/{self.ref.UID()}"}
        }
        notify(ObjectModifiedEvent(self.document))

        references = self.get_references()
        reference = references[0]

        self.assertEqual(len(references), 1)
        self.assertEqual(len(reference["sources"]), 1)
        self.assertEqual(reference["sources"][0]["uid"], self.document.UID())
        self.assertEqual(reference["target"]["uid"], self.ref.UID())

    def test_icon_block_background_link_integrity(self):
        self.assertEqual(self.get_references(), [])
        self.document.blocks = {
            "xyz": {"@type": "iconBlocks", "background": [self.ref.UID()]}
        }
        notify(ObjectModifiedEvent(self.document))

        references = self.get_references()
        reference = references[0]

        self.assertEqual(len(references), 1)
        self.assertEqual(len(reference["sources"]), 1)
        self.assertEqual(reference["sources"][0]["uid"], self.document.UID())
        self.assertEqual(reference["target"]["uid"], self.ref.UID())

    def test_icon_block_subblocks_text_link_integrity(self):
        self.assertEqual(self.get_references(), [])
        self.document.blocks = {
            "xyz": {
                "@type": "iconBlocks",
                "subblocks": [
                    {
                        "text": [
                            {
                                "type": "p",
                                "children": [
                                    {
                                        "type": "link",
                                        "data": {
                                            "url": f"/resolveuid/{self.ref.UID()}",
                                        },
                                        "children": [{"text": "foo"}],
                                    },
                                ],
                            }
                        ]
                    }
                ],
            }
        }
        notify(ObjectModifiedEvent(self.document))

        references = self.get_references()
        reference = references[0]

        self.assertEqual(len(references), 1)
        self.assertEqual(len(reference["sources"]), 1)
        self.assertEqual(reference["sources"][0]["uid"], self.document.UID())
        self.assertEqual(reference["target"]["uid"], self.ref.UID())

    def test_icon_block_subblocks_href_link_integrity(self):
        self.assertEqual(self.get_references(), [])
        self.document.blocks = {
            "xyz": {
                "@type": "iconBlocks",
                "subblocks": [{"href": f"/resolveuid/{self.ref.UID()}"}],
            }
        }
        notify(ObjectModifiedEvent(self.document))

        references = self.get_references()
        reference = references[0]

        self.assertEqual(len(references), 1)
        self.assertEqual(len(reference["sources"]), 1)
        self.assertEqual(reference["sources"][0]["uid"], self.document.UID())
        self.assertEqual(reference["target"]["uid"], self.ref.UID())

    def test_listing_block_linkHref_link_integrity(self):
        self.assertEqual(self.get_references(), [])
        self.document.blocks = {
            "xyz": {
                "@type": "listing",
                "linkHref": [
                    {
                        "@id": f"resolveuid/{self.ref.UID()}",
                        "Description": "",
                        "Title": "PAgina da linkare",
                        "title": "PAgina da linkare",
                    }
                ],
            }
        }
        notify(ObjectModifiedEvent(self.document))

        references = self.get_references()
        reference = references[0]

        self.assertEqual(len(references), 1)
        self.assertEqual(len(reference["sources"]), 1)
        self.assertEqual(reference["sources"][0]["uid"], self.document.UID())
        self.assertEqual(reference["target"]["uid"], self.ref.UID())

    def test_rss_block_linkMore_link_integrity(self):
        self.assertEqual(self.get_references(), [])
        self.document.blocks = {
            "xyz": {"@type": "rssBlock", "linkMore": f"resolveuid/{self.ref.UID()}"}
        }
        notify(ObjectModifiedEvent(self.document))

        references = self.get_references()
        reference = references[0]

        self.assertEqual(len(references), 1)
        self.assertEqual(len(reference["sources"]), 1)
        self.assertEqual(reference["sources"][0]["uid"], self.document.UID())
        self.assertEqual(reference["target"]["uid"], self.ref.UID())

    def test_audio_block_link_integrity(self):
        self.assertEqual(self.get_references(), [])
        self.document.blocks = {
            "xyz": {"@type": "audioBlock", "audio": [{"UID": self.ref.UID()}]}
        }
        notify(ObjectModifiedEvent(self.document))
        references = self.get_references()
        reference = references[0]

        self.assertEqual(len(references), 1)
        self.assertEqual(len(reference["sources"]), 1)
        self.assertEqual(reference["sources"][0]["uid"], self.document.UID())
        self.assertEqual(reference["target"]["uid"], self.ref.UID())

    def test_count_down_text_link_integrity(self):
        self.assertEqual(self.get_references(), [])
        self.document.blocks = {
            "xyz": {
                "@type": "count_down",
                "text": [
                    {
                        "type": "p",
                        "children": [
                            {
                                "type": "link",
                                "data": {
                                    "url": f"/resolveuid/{self.ref.UID()}",
                                },
                                "children": [{"text": "foo"}],
                            },
                        ],
                    }
                ],
            }
        }
        notify(ObjectModifiedEvent(self.document))

        references = self.get_references()
        reference = references[0]

        self.assertEqual(len(references), 1)
        self.assertEqual(len(reference["sources"]), 1)
        self.assertEqual(reference["sources"][0]["uid"], self.document.UID())
        self.assertEqual(reference["target"]["uid"], self.ref.UID())

    def test_count_down_countdown_text_link_integrity(self):
        self.assertEqual(self.get_references(), [])
        self.document.blocks = {
            "xyz": {
                "@type": "count_down",
                "countdown_text": [
                    {
                        "type": "p",
                        "children": [
                            {
                                "type": "link",
                                "data": {
                                    "url": f"/resolveuid/{self.ref.UID()}",
                                },
                                "children": [{"text": "foo"}],
                            },
                        ],
                    }
                ],
            }
        }
        notify(ObjectModifiedEvent(self.document))

        references = self.get_references()
        reference = references[0]

        self.assertEqual(len(references), 1)
        self.assertEqual(len(reference["sources"]), 1)
        self.assertEqual(reference["sources"][0]["uid"], self.document.UID())
        self.assertEqual(reference["target"]["uid"], self.ref.UID())
