# -*- coding: utf-8 -*-
from Products.CMFPlone.interfaces import INonInstallable
from Products.CMFPlone.utils import get_installer
from plone import api
from zope.interface import implementer

import json


homepage_en = {
    "blocks": {
        "03e4de7a-d866-4140-86a6-b72c7e2e566f": {
            "@type": "title",
            "href": "",
            "url": "",
        },
        "0d2162c7-ad5b-456f-85f0-ed0ba6237b38": {
            "@type": "text",
            "text": {
                "blocks": [
                    {
                        "data": {},
                        "depth": 0,
                        "entityRanges": [],
                        "inlineStyleRanges": [],
                        "key": "1mqjm",
                        "text": "2020 - Volto Team - Plone Foundation",
                        "type": "unstyled",
                    }
                ],
                "entityMap": {},
            },
        },
        "18c2a5e5-01dc-4e2a-88ac-d121622c0beb": {
            "@type": "text",
            "text": {
                "blocks": [
                    {
                        "key": "br6kt",
                        "text": "Volto  is a React-based frontend for content management systems, currently  supporting three backend implementations: Plone, Guillotina and a NodeJS  reference implementation.",  #  noqa
                        "type": "unstyled",
                        "depth": 0,
                        "inlineStyleRanges": [],
                        "entityRanges": [{"offset": 0, "length": 5, "key": 0}],
                        "data": {},
                    }
                ],
                "entityMap": {
                    "0": {
                        "type": "LINK",
                        "mutability": "MUTABLE",
                        "data": {"url": "https://github.com/plone/volto"},
                    }
                },
            },
        },
        "3a378af0-3253-485f-a332-d8ac553a9750": {
            "@type": "text",
            "text": {
                "blocks": [
                    {
                        "key": "diiac",
                        "text": "Plone  is a CMS built on Python with over 19 years of experience. Plone has  very interesting features that appeal to developers and users alike,  such as customizable content types, hierarchical URL object traversing  and a sophisticated content workflow powered by a granular permissions  model. This allows you to build anything from simple websites to  enterprise-grade intranets. Volto exposes all these features and  communicates with Plone via its mature REST API. Volto can be esily themed and is highly customizable.",  #  noqa
                        "type": "unstyled",
                        "depth": 0,
                        "inlineStyleRanges": [],
                        "entityRanges": [
                            {"offset": 0, "length": 5, "key": 0},
                            {"offset": 462, "length": 8, "key": 1},
                        ],
                        "data": {},
                    }
                ],
                "entityMap": {
                    "0": {
                        "type": "LINK",
                        "mutability": "MUTABLE",
                        "data": {"url": "https://plone.org/"},
                    },
                    "1": {
                        "type": "LINK",
                        "mutability": "MUTABLE",
                        "data": {
                            "url": "https://github.com/plone/plone.restapi"
                        },
                    },
                },
            },
        },
        "4ba13f95-1f48-4d3c-ae9f-484717f411d0": {
            "@type": "text",
            "text": {
                "blocks": [
                    {
                        "key": "dibnf",
                        "text": "This Volto installation works with the last Plone 5.2  running on Python 3.",  # noqa
                        "type": "unstyled",
                        "depth": 0,
                        "inlineStyleRanges": [],
                        "entityRanges": [],
                        "data": {},
                    }
                ],
                "entityMap": {},
            },
        },
        "6a7f13c6-d06c-4400-b0f8-f0bb81d38287": {"@type": "text"},
        "77387955-0cf7-4045-9fff-28b74c05a07b": {
            "@type": "text",
            "text": {
                "blocks": [
                    {
                        "key": "d0084",
                        "text": "Start using Volto",
                        "type": "header-three",
                        "depth": 0,
                        "inlineStyleRanges": [],
                        "entityRanges": [],
                        "data": {},
                    }
                ],
                "entityMap": {},
            },
        },
        "7ef4018b-0c87-42a7-a5b8-1524207de7b9": {
            "@type": "text",
            "text": {
                "blocks": [
                    {
                        "key": "9ngcf",
                        "text": "Volto also supports other APIs like Guillotina,  a Python resource management system, inspired by Plone and using the  same basic concepts like traversal, content types and permissions model.",  # noqa
                        "type": "unstyled",
                        "depth": 0,
                        "inlineStyleRanges": [],
                        "entityRanges": [
                            {"offset": 36, "length": 10, "key": 0}
                        ],
                        "data": {},
                    }
                ],
                "entityMap": {
                    "0": {
                        "type": "LINK",
                        "mutability": "MUTABLE",
                        "data": {"url": "https://guillotina.io/"},
                    }
                },
            },
        },
        "84aba93f-07ca-4488-82d1-bf7c7918f446": {"@type": "text"},
        "8cb27f18-0183-4851-8354-273e33a9e1de": {
            "@type": "text",
            "text": {
                "blocks": [
                    {
                        "key": "10ka1",
                        "text": "Have fun!",
                        "type": "unstyled",
                        "depth": 0,
                        "inlineStyleRanges": [],
                        "entityRanges": [],
                        "data": {},
                    }
                ],
                "entityMap": {},
            },
        },
        "9a072abf-4b2c-4f8d-88ec-162ce048e0d9": {"@type": "text"},
        "c113ab86-8f39-439f-b80d-72c52aeabca6": {
            "@type": "text",
            "text": {
                "blocks": [
                    {
                        "key": "4e9ig",
                        "text": "Last but not least, it also supports a Volto Nodejs-based backend reference API implementation that demos how other systems could also use Volto to display and create content through it.",  # noqa
                        "type": "unstyled",
                        "depth": 0,
                        "inlineStyleRanges": [],
                        "entityRanges": [
                            {"offset": 39, "length": 36, "key": 0}
                        ],
                        "data": {},
                    }
                ],
                "entityMap": {
                    "0": {
                        "type": "LINK",
                        "mutability": "MUTABLE",
                        "data": {
                            "url": "https://github.com/plone/volto-reference-backend"
                        },
                    }
                },
            },
        },
        "c1709dc0-8f54-431b-9d5c-927820fd9823": {
            "@type": "text",
            "text": {
                "blocks": [
                    {
                        "key": "17fir",
                        "text": "This is the default homepage. Customize it and start using Volto!",
                        "type": "unstyled",
                        "depth": 0,
                        "inlineStyleRanges": [],
                        "entityRanges": [],
                        "data": {},
                    }
                ],
                "entityMap": {},
            },
        },
    },
    "blocks_layout": {
        "items": [
            "03e4de7a-d866-4140-86a6-b72c7e2e566f",
            "84aba93f-07ca-4488-82d1-bf7c7918f446",
            "18c2a5e5-01dc-4e2a-88ac-d121622c0beb",
            "3a378af0-3253-485f-a332-d8ac553a9750",
            "7ef4018b-0c87-42a7-a5b8-1524207de7b9",
            "c113ab86-8f39-439f-b80d-72c52aeabca6",
            "4ba13f95-1f48-4d3c-ae9f-484717f411d0",
            "6a7f13c6-d06c-4400-b0f8-f0bb81d38287",
            "77387955-0cf7-4045-9fff-28b74c05a07b",
            "c1709dc0-8f54-431b-9d5c-927820fd9823",
            "9a072abf-4b2c-4f8d-88ec-162ce048e0d9",
            "8cb27f18-0183-4851-8354-273e33a9e1de",
            "0d2162c7-ad5b-456f-85f0-ed0ba6237b38",
        ]
    },
}

homepage_it = {
    "blocks": {
        "03e4de7a-d866-4140-86a6-b72c7e2e566f": {
            "@type": "title",
            "href": "",
            "url": "",
        },
        "0d2162c7-ad5b-456f-85f0-ed0ba6237b38": {
            "@type": "text",
            "text": {
                "blocks": [
                    {
                        "data": {},
                        "depth": 0,
                        "entityRanges": [],
                        "inlineStyleRanges": [],
                        "key": "1mqjm",
                        "text": "2020 - Volto Team - Plone Foundation",
                        "type": "unstyled",
                    }
                ],
                "entityMap": {},
            },
        },
        "18c2a5e5-01dc-4e2a-88ac-d121622c0beb": {
            "@type": "text",
            "text": {
                "blocks": [
                    {
                        "data": {},
                        "depth": 0,
                        "entityRanges": [{"key": 0, "length": 5, "offset": 0}],
                        "inlineStyleRanges": [],
                        "key": "br6kt",
                        "text": "Volto \u00e8 un frontend basato su React per i sistemi di gestione dei contenuti, che attualmente supporta tre implementazioni di back-end: Plone, Guillotina e un'implementazione di riferimento di NodeJS.",  # noqa
                        "type": "unstyled",
                    }
                ],
                "entityMap": {
                    "0": {
                        "data": {
                            "href": "https://github.com/plone/volto",
                            "url": "https://github.com/plone/volto",
                        },
                        "mutability": "MUTABLE",
                        "type": "LINK",
                    }
                },
            },
        },
        "3a378af0-3253-485f-a332-d8ac553a9750": {
            "@type": "text",
            "text": {
                "blocks": [
                    {
                        "data": {},
                        "depth": 0,
                        "entityRanges": [
                            {"key": 0, "length": 5, "offset": 0},
                            {"key": 1, "length": 8, "offset": 503},
                        ],
                        "inlineStyleRanges": [],
                        "key": "diiac",
                        "text": "Plone \u00e8 un CMS basato su Python con oltre 19 anni di esperienza. Plone ha caratteristiche molto interessanti che piacciono sia agli sviluppatori che agli utenti, come tipi di contenuto personalizzabili, attraversamento gerarchico di oggetti URL e un workflow sui contenuti sofisticato basato su un modello granulare di autorizzazioni. Ci\u00f2 consente di creare qualsiasi cosa, da semplici siti Web a intranet di livello aziendale. Volto espone tutte queste funzionalit\u00e0 e comunica con Plone tramite le sue REST API matura. Volto ha un tema facilmente estendibile ed \u00e8 altamente personalizzabile.",  # noqa
                        "type": "unstyled",
                    }
                ],
                "entityMap": {
                    "0": {
                        "data": {
                            "href": "https://plone.org/",
                            "url": "https://plone.org/",
                        },
                        "mutability": "MUTABLE",
                        "type": "LINK",
                    },
                    "1": {
                        "data": {
                            "href": "https://github.com/plone/plone.restapi",
                            "url": "https://github.com/plone/plone.restapi",
                        },
                        "mutability": "MUTABLE",
                        "type": "LINK",
                    },
                },
            },
        },
        "4ba13f95-1f48-4d3c-ae9f-484717f411d0": {
            "@type": "text",
            "text": {
                "blocks": [
                    {
                        "data": {},
                        "depth": 0,
                        "entityRanges": [],
                        "inlineStyleRanges": [],
                        "key": "dibnf",
                        "text": "Questa installazione di Volto prevede l'ultimo Plone 5.2 in esecuzione su Python 3.",  #  noqa
                        "type": "unstyled",
                    }
                ],
                "entityMap": {},
            },
        },
        "6a7f13c6-d06c-4400-b0f8-f0bb81d38287": {"@type": "text"},
        "77387955-0cf7-4045-9fff-28b74c05a07b": {
            "@type": "text",
            "text": {
                "blocks": [
                    {
                        "data": {},
                        "depth": 0,
                        "entityRanges": [],
                        "inlineStyleRanges": [],
                        "key": "d0084",
                        "text": "Inizia ad utilizzare Volto",
                        "type": "header-three",
                    }
                ],
                "entityMap": {},
            },
        },
        "7ef4018b-0c87-42a7-a5b8-1524207de7b9": {
            "@type": "text",
            "text": {
                "blocks": [
                    {
                        "data": {},
                        "depth": 0,
                        "entityRanges": [
                            {"key": 0, "length": 10, "offset": 36}
                        ],
                        "inlineStyleRanges": [],
                        "key": "9ngcf",
                        "text": "Volto supporta anche altre API come Guillotina, un sistema di gestione delle risorse Python, ispirato a Plone e che utilizza gli stessi concetti di base come traversing, tipi di contenuto e modello di autorizzazioni.",  #  noqa
                        "type": "unstyled",
                    }
                ],
                "entityMap": {
                    "0": {
                        "data": {
                            "href": "https://guillotina.io/",
                            "url": "https://guillotina.io/",
                        },
                        "mutability": "MUTABLE",
                        "type": "LINK",
                    }
                },
            },
        },
        "8cb27f18-0183-4851-8354-273e33a9e1de": {
            "@type": "text",
            "text": {
                "blocks": [
                    {
                        "data": {},
                        "depth": 0,
                        "entityRanges": [],
                        "inlineStyleRanges": [],
                        "key": "10ka1",
                        "text": "Buon divertimento!",
                        "type": "unstyled",
                    }
                ],
                "entityMap": {},
            },
        },
        "9a072abf-4b2c-4f8d-88ec-162ce048e0d9": {"@type": "text"},
        "c113ab86-8f39-439f-b80d-72c52aeabca6": {
            "@type": "text",
            "text": {
                "blocks": [
                    {
                        "data": {},
                        "depth": 0,
                        "entityRanges": [],
                        "inlineStyleRanges": [],
                        "key": "4e9ig",
                        "text": "Infine, Volto supporta anche un'implementazione dell'API backend di riferimento basata su Nodejs che dimostra come anche altri sistemi potrebbero utilizzare Volto per visualizzare e creare contenuti attraverso di esso.",  # noqa
                        "type": "unstyled",
                    }
                ],
                "entityMap": {},
            },
        },
        "c1709dc0-8f54-431b-9d5c-927820fd9823": {
            "@type": "text",
            "text": {
                "blocks": [
                    {
                        "data": {},
                        "depth": 0,
                        "entityRanges": [],
                        "inlineStyleRanges": [],
                        "key": "17fir",
                        "text": "Questa \u00e8 l'homepage di  default. Personalizzala e inizia ad utilizzare Volto!",  # noqa
                        "type": "unstyled",
                    }
                ],
                "entityMap": {},
            },
        },
        "84aba93f-07ca-4488-82d1-bf7c7918f446": {"@type": "text"},
    },
    "blocks_layout": {
        "items": [
            "03e4de7a-d866-4140-86a6-b72c7e2e566f",
            "84aba93f-07ca-4488-82d1-bf7c7918f446",
            "18c2a5e5-01dc-4e2a-88ac-d121622c0beb",
            "3a378af0-3253-485f-a332-d8ac553a9750",
            "7ef4018b-0c87-42a7-a5b8-1524207de7b9",
            "c113ab86-8f39-439f-b80d-72c52aeabca6",
            "4ba13f95-1f48-4d3c-ae9f-484717f411d0",
            "6a7f13c6-d06c-4400-b0f8-f0bb81d38287",
            "77387955-0cf7-4045-9fff-28b74c05a07b",
            "c1709dc0-8f54-431b-9d5c-927820fd9823",
            "9a072abf-4b2c-4f8d-88ec-162ce048e0d9",
            "8cb27f18-0183-4851-8354-273e33a9e1de",
            "0d2162c7-ad5b-456f-85f0-ed0ba6237b38",
        ]
    },
}


@implementer(INonInstallable)
class HiddenProfiles(object):
    def getNonInstallableProfiles(self):
        """Hide uninstall profile from site-creation and quickinstaller."""
        return ["redturtle.volto:uninstall"]


def post_install(context):
    """Post install script"""
    portal = api.portal.get()

    is_pam_installed = get_installer(
        portal, context.REQUEST
    ).isProductInstalled("plone.app.multilingual")

    create_root_homepage()

    if is_pam_installed:
        create_lrf_homepages()


def uninstall(context):
    """Uninstall script"""
    # Do something at the end of the uninstallation of this package.


def create_root_homepage():
    """ create default homepage """
    portal = api.portal.get()

    portal.setTitle("Benvenuto in Volto!")
    portal.setDescription("Il sistema di gestione contenuti basato su React")

    if not getattr(portal, "blocks", False):
        portal.manage_addProperty(
            "blocks", json.dumps(homepage_it["blocks"]), "string"
        )

    if not getattr(portal, "blocks_layout", False):
        portal.manage_addProperty(
            "blocks_layout", json.dumps(homepage_it["blocks_layout"]), "string"
        )


def create_lrf_homepages():
    portal = api.portal.get()

    portal.it.blocks = homepage_it["blocks"]
    portal.it.blocks_layout = homepage_it["blocks_layout"]
    portal.it.setTitle("Benvenuto in Volto!")
    portal.it.setDescription(
        "Il sistema di gestione contenuti basato su React"
    )

    portal.en.blocks = homepage_en["blocks"]
    portal.en.blocks_layout = homepage_en["blocks_layout"]
    portal.en.setTitle("Welcome to Volto!")
    portal.en.setDescription("The React powered content management system")
