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

    def test_accordion_block_indexed_with_draftjs(self):
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

    def test_accordion_block_indexed(self):
        search_words = [
            "accordiondescription",
            "accordiontext1",
            "accordiontitle1",
            "accordiontext2",
            "accordiontitle2",
            "accordiontitle",
        ]

        for word in search_words:
            self.assertEqual(len(api.content.find(SearchableText=word)), 0)

        self.document.blocks = {
            "xyz": {
                "@type": "accordion",
                "description": [
                    {"children": [{"text": "accordiondescription"}], "type": "p"}
                ],
                "subblocks": [
                    {
                        "id": "1728994537150",
                        "text": [
                            {"children": [{"text": "accordiontext1"}], "type": "p"}
                        ],
                        "title": "accordiontitle1",
                    },
                    {
                        "id": "1728994561878",
                        "text": [
                            {
                                "children": [{"text": "accordiontext2"}],
                                "type": "p",
                            }
                        ],
                        "title": "accordiontitle2",
                    },
                ],
                "title": "accordiontitle",
            }
        }

        self.document.blocks_layout = {"items": ["xyz"]}
        self.document.reindexObject()
        commit()
        for word in search_words:
            res = api.content.find(SearchableText=word)
            self.assertEqual(len(res), 1)
            self.assertEqual(res[0].UID, self.document.UID())

    def test_alert_block_indexed_with_draftjs(self):
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

    def test_alert_block_indexed(self):
        search_words = [
            "ALERTTEXT",
        ]

        for word in search_words:
            self.assertEqual(len(api.content.find(SearchableText=word)), 0)

        self.document.blocks = {
            "xyz": {
                "@type": "alert",
                "text": [
                    {
                        "children": [
                            {"text": "ALE"},
                            {"children": [{"text": "RTTE"}], "type": "strong"},
                            {"text": "XT"},
                        ],
                        "type": "p",
                    }
                ],
            }
        }

        self.document.blocks_layout = {"items": ["xyz"]}
        self.document.reindexObject()
        commit()
        for word in search_words:
            res = api.content.find(SearchableText=word)
            self.assertEqual(len(res), 1)
            self.assertEqual(res[0].UID, self.document.UID())

    def test_simple_card_block_indexed_with_draftjs(self):
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

    def test_simple_card_block_indexed(self):
        search_words = [
            "simplecardtitle",
            "simplecarddescription",
        ]

        for word in search_words:
            self.assertEqual(len(api.content.find(SearchableText=word)), 0)

        self.document.blocks = {
            "xyz": {
                "@type": "testo_riquadro_semplice",
                "simple_card_content": [
                    {"children": [{"text": "simplecarddescription"}], "type": "p"}
                ],
                "simple_card_title": "simplecardtitle",
            },
        }

        self.document.blocks_layout = {"items": ["xyz"]}
        self.document.reindexObject()
        commit()

        for word in search_words:
            res = api.content.find(SearchableText=word)
            self.assertEqual(len(res), 1)
            self.assertEqual(res[0].UID, self.document.UID())

    def test_card_with_image_block_indexed_with_draftjs(self):
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

    def test_card_with_image_block_indexed(self):
        search_words = [
            "cardwithimagetitle",
            "cardwithimagetext",
        ]

        for word in search_words:
            self.assertEqual(len(api.content.find(SearchableText=word)), 0)

        self.document.blocks = {
            "xyz": {
                "@type": "testo_riquadro_immagine",
                "image_card_content": [
                    {"children": [{"text": "cardwithimagetext"}], "type": "p"}
                ],
                "image_card_title": "cardwithimagetitle",
            },
        }

        self.document.blocks_layout = {"items": ["xyz"]}
        self.document.reindexObject()
        commit()

        for word in search_words:
            res = api.content.find(SearchableText=word)
            self.assertEqual(len(res), 1)
            self.assertEqual(res[0].UID, self.document.UID())

    def test_callout_block_indexed(self):
        self.assertEqual(len(api.content.find(SearchableText="callouttitle")), 0)
        self.assertEqual(len(api.content.find(SearchableText="callouttext")), 0)

        self.document.blocks = {
            "xyz": {
                "@type": "callout_block",
                "text": [{"children": [{"text": "callouttext"}], "type": "p"}],
                "title": "callouttitle",
            },
        }
        self.document.blocks_layout = {"items": ["xyz"]}
        self.document.reindexObject()
        commit()

        self.assertEqual(len(api.content.find(SearchableText="callouttitle")), 1)
        self.assertEqual(len(api.content.find(SearchableText="callouttext")), 1)
        self.assertEqual(
            api.content.find(SearchableText="callouttitle")[0].UID, self.document.UID()
        )
        self.assertEqual(
            api.content.find(SearchableText="callouttext")[0].UID, self.document.UID()
        )

    def test_slate_table_block_indexed(self):
        search_words = [
            "tableheader1",
            "tableheader2",
            "tablecontent1",
            "tablecontent2",
            "tablecontentwithstyles",
        ]

        for word in search_words:
            self.assertEqual(len(api.content.find(SearchableText=word)), 0)

        self.document.blocks = {
            "xyz": {
                "@type": "slateTable",
                "table": {
                    "rows": [
                        {
                            "cells": [
                                {
                                    "key": "aaca3",
                                    "type": "header",
                                    "value": [
                                        {
                                            "children": [{"text": "tableheader1"}],
                                            "type": "p",
                                        }
                                    ],
                                },
                                {
                                    "key": "8l7b7",
                                    "type": "header",
                                    "value": [
                                        {
                                            "children": [{"text": "tableheader2"}],
                                            "type": "p",
                                        }
                                    ],
                                },
                            ],
                            "key": "d9fc8",
                        },
                        {
                            "cells": [
                                {
                                    "key": "8jqta",
                                    "type": "data",
                                    "value": [
                                        {
                                            "children": [
                                                {"text": "tablecontent1 tableco"},
                                                {
                                                    "children": [{"text": "ntentw"}],
                                                    "type": "strong",
                                                },
                                                {"text": "ithstyles"},
                                            ],
                                            "type": "p",
                                        }
                                    ],
                                },
                                {
                                    "key": "9rhfa",
                                    "type": "data",
                                    "value": [
                                        {
                                            "children": [{"text": "tablecontent2"}],
                                            "type": "p",
                                        }
                                    ],
                                },
                            ],
                            "key": "51rjk",
                        },
                    ],
                },
            },
        }
        self.document.blocks_layout = {"items": ["xyz"]}
        self.document.reindexObject()
        commit()

        for word in search_words:
            res = api.content.find(SearchableText=word)
            self.assertEqual(len(res), 1)
            self.assertEqual(res[0].UID, self.document.UID())

    def test_numbers_block_indexed(self):
        search_words = [
            "numblockstitle",
            "numberdescription",
            "numbertitle",
        ]

        for word in search_words:
            self.assertEqual(len(api.content.find(SearchableText=word)), 0)

        self.document.blocks = {
            "xyz": {
                "@type": "numbersBlock",
                "subblocks": [
                    {
                        "id": "1729000093544",
                        "text": "numberdescription",
                        "title": "numbertitle",
                    },
                ],
                "title": "numblockstitle",
            },
        }

        self.document.blocks_layout = {"items": ["xyz"]}
        self.document.reindexObject()
        commit()

        for word in search_words:
            res = api.content.find(SearchableText=word)
            self.assertEqual(len(res), 1)
            self.assertEqual(res[0].UID, self.document.UID())

    def test_grid_block_indexed(self):
        search_words = [
            "grid1text",
            "grid2",
            "grid22",
        ]

        for word in search_words:
            self.assertEqual(len(api.content.find(SearchableText=word)), 0)

        self.document.blocks = {
            "xyz": {
                "@type": "gridBlock",
                "blocks": {
                    "0a652dc2-f47a-4760-80ce-3aacb2b94256": {
                        "@type": "slate",
                        "plaintext": "grid1text",
                        "value": [{"children": [{"text": "grid1text"}], "type": "p"}],
                    },
                    "c11274a4-6886-41f6-8e5e-615ae9c5dc84": {
                        "@type": "slate",
                        "plaintext": "grid2\ngrid22",
                        "value": [
                            {
                                "children": [{"text": "grid2\ngrid22"}],
                                "type": "p",
                            },
                        ],
                    },
                },
            },
        }

        self.document.blocks_layout = {"items": ["xyz"]}
        self.document.reindexObject()
        commit()

        for word in search_words:
            res = api.content.find(SearchableText=word)
            self.assertEqual(len(res), 1)
            self.assertEqual(res[0].UID, self.document.UID())

    def test_hero_block_indexed(self):
        search_words = [
            "herodescription",
            "herotitle",
        ]

        for word in search_words:
            self.assertEqual(len(api.content.find(SearchableText=word)), 0)

        self.document.blocks = {
            "xyz": {
                "@type": "hero",
                "description": "herodescription",
                "title": "herotitle",
            },
        }

        self.document.blocks_layout = {"items": ["xyz"]}
        self.document.reindexObject()
        commit()

        for word in search_words:
            res = api.content.find(SearchableText=word)
            self.assertEqual(len(res), 1)
            self.assertEqual(res[0].UID, self.document.UID())

    def test_icon_block_indexed(self):
        search_words = [
            "iconblocksdescription",
            "icon1description",
            "icon1title",
            "icon2description",
            "icon2title",
            "iconblocktitle",
        ]

        for word in search_words:
            self.assertEqual(len(api.content.find(SearchableText=word)), 0)

        self.document.blocks = {
            "xyz": {
                "@type": "iconBlocks",
                "description": [
                    {"children": [{"text": "iconblocksdescription"}], "type": "p"}
                ],
                "subblocks": [
                    {
                        "id": "1728999889749",
                        "text": [
                            {"children": [{"text": "icon1description"}], "type": "p"}
                        ],
                        "title": "icon1title",
                    },
                    {
                        "id": "1728999916864",
                        "text": [
                            {"children": [{"text": "icon2description"}], "type": "p"}
                        ],
                        "title": "icon2title",
                    },
                ],
                "title": "iconblocktitle",
            }
        }

        self.document.blocks_layout = {"items": ["xyz"]}
        self.document.reindexObject()
        commit()

        for word in search_words:
            res = api.content.find(SearchableText=word)
            self.assertEqual(len(res), 1)
            self.assertEqual(res[0].UID, self.document.UID())

    def test_cta_block_indexed(self):
        search_words = [
            "ctatitle",
            "ctatext",
            "ctatextwithstyle",
            "ctatextwithlink",
        ]

        for word in search_words:
            self.assertEqual(len(api.content.find(SearchableText=word)), 0)

        self.document.blocks = {
            "xyz": {
                "@type": "cta_block",
                "cta_content": [
                    {
                        "children": [
                            {"text": "ctatext "},
                            {"children": [{"text": "ctatext"}], "type": "em"},
                            {"text": "withstyle ctatextwith"},
                            {
                                "children": [{"text": "link"}],
                                "data": {
                                    "dataElement": "",
                                    "url": "http://www.google.it",
                                },
                                "type": "link",
                            },
                        ],
                        "type": "p",
                    }
                ],
                "cta_title": "ctatitle",
            }
        }

        self.document.blocks_layout = {"items": ["xyz"]}
        self.document.reindexObject()
        commit()
        for word in search_words:
            res = api.content.find(SearchableText=word)
            self.assertEqual(len(res), 1)
            self.assertEqual(res[0].UID, self.document.UID())

    def test_contacts_block_indexed(self):
        search_words = [
            "contactsdescription",
            "contacts",
            "contactsmail",
            "com",
            "1111111111",
            "contacttextwithstyle",
            "contacttitle",
            "contactsblocktitle",
        ]

        for word in search_words:
            self.assertEqual(len(api.content.find(SearchableText=word)), 0)

        self.document.blocks = {
            "xyz": {
                "@type": "contacts",
                "description": [
                    {
                        "children": [{"text": "contactsdescription"}],
                        "type": "p",
                    }
                ],
                "subblocks": [
                    {
                        "email": [
                            {
                                "children": [{"text": "contacts@contactsmail.com"}],
                                "type": "p",
                            }
                        ],
                        "id": "1728999173272",
                        "tel": [{"children": [{"text": "1111111111"}], "type": "p"}],
                        "text": [
                            {
                                "children": [
                                    {"text": "contacttext contact"},
                                    {"children": [{"text": "tex"}], "type": "u"},
                                    {"text": "twithstyle"},
                                ],
                                "type": "p",
                            }
                        ],
                        "title": "contacttitle",
                    }
                ],
                "title": "contactsblocktitle",
            }
        }

        self.document.blocks_layout = {"items": ["xyz"]}
        self.document.reindexObject()
        commit()
        for word in search_words:
            res = api.content.find(SearchableText=word)
            self.assertEqual(len(res), 1)
            self.assertEqual(res[0].UID, self.document.UID())

    def test_remote_counter_block_indexed(self):
        search_words = [
            "countertext",
            "countertitle",
        ]

        for word in search_words:
            self.assertEqual(len(api.content.find(SearchableText=word)), 0)

        self.document.blocks = {
            "xyz": {
                "@type": "remote-counter",
                "text": [{"type": "p", "children": [{"text": "countertext"}]}],
                "title": [{"type": "p", "children": [{"text": "countertitle"}]}],
            }
        }

        self.document.blocks_layout = {"items": ["xyz"]}
        self.document.reindexObject()
        commit()
        for word in search_words:
            res = api.content.find(SearchableText=word)
            self.assertEqual(len(res), 1)
            self.assertEqual(res[0].UID, self.document.UID())

    def test_countdown_block_indexed(self):
        search_words = [
            "countdowntitle",
            "countdowntext",
        ]

        for word in search_words:
            self.assertEqual(len(api.content.find(SearchableText=word)), 0)

        self.document.blocks = {
            "xyz": {
                "@type": "count_down",
                "countdown_text": [
                    {
                        "children": [{"text": "countdowntext"}],
                        "styleName": "text-center",
                        "type": "p",
                    }
                ],
                "text": [{"children": [{"text": "countdowntitle"}], "type": "h2"}],
            }
        }

        self.document.blocks_layout = {"items": ["xyz"]}
        self.document.reindexObject()
        commit()
        for word in search_words:
            res = api.content.find(SearchableText=word)
            self.assertEqual(len(res), 1)
            self.assertEqual(res[0].UID, self.document.UID())
