# -*- coding: utf-8 -*-
from copy import deepcopy
from Products.Five import BrowserView
from plone import api
from Acquisition import aq_base
from plone.dexterity.utils import iterSchemata
from zope.schema import getFieldsInOrder

import logging
import json

logger = logging.getLogger(__name__)

BLOCKS = [
    {"id": "accordion", "title": "Accordion"},
    {"id": "alert", "title": "Alert"},
    {"id": "argumentsInEvidence", "title": "Argomenti in evidenza"},
    {"id": "break", "title": "Interruzione di pagina"},
    {"id": "calendar", "title": "Calendario"},
    {"id": "contacts", "title": "Contatti"},
    {"id": "count_down", "title": "Count Down"},
    {"id": "cta_block", "title": "Blocco CTA"},
    {"id": "form", "title": "Form"},
    {"id": "highlitedContent", "title": "Contenuto in primo piano"},
    {"id": "html", "title": "HTML"},
    {"id": "iconBlocks", "title": "Blocchi con icone"},
    {"id": "image", "title": "Immagine"},
    {"id": "listing", "title": "Elenco"},
    {"id": "maps", "title": "Maps"},
    {"id": "numbersBlock", "title": "Blocco Numeri"},
    {"id": "rss", "title": "RSS"},
    {"id": "rss", "title": "RSS"},
    {"id": "searchBandi", "title": "Ricerca bandi"},
    {"id": "searchEvents", "title": "Ricerca eventi"},
    {"id": "searchSections", "title": "Ricerca nelle sezioni"},
    {"id": "searchUO", "title": "Ricerca Unità Organizzative"},
    {"id": "table", "title": "Tabella"},
    {"id": "testo_riquadro_immagine", "title": "Card con immagine"},
    {"id": "testo_riquadro_semplice", "title": "Card semplice"},
    {"id": "text", "title": "Testo"},
    {"id": "twitter_posts", "title": "Twitter posts"},
    {"id": "video_gallery", "title": "Video Gallery"},
    {"id": "video", "title": "Video"},
]


class View(BrowserView):

    results = {}

    def __call__(self):
        submitted = self.request.form.get("search", None)
        text = self.request.form.get("pattern", "")
        custom_block_type = self.request.form.get("custom_block_type", "")
        block_type = self.request.form.get("block_type", "")

        if custom_block_type:
            block_type = custom_block_type
        if not submitted:
            return super().__call__()

        portal_catalog = api.portal.get_tool("portal_catalog")
        results = portal_catalog()
        tot = len(results)
        i = 0
        found = []
        logger.info("## START ##")
        for brain in results:
            if (i + 1) % 200 == 0:
                logger.info(" - Progress {}/{}".format(i + 1, tot))
            item = brain.getObject()
            aq_base_obj = aq_base(item)
            for schemata in iterSchemata(aq_base_obj):
                for name, field in getFieldsInOrder(schemata):
                    if name in ["blocks_layout"]:
                        continue
                    value = getattr(aq_base_obj, name, None)
                    if isinstance(value, str) or isinstance(value, dict):
                        res = self.has_block(
                            block_type=block_type, data=value, text=text
                        )
                    else:
                        continue
                    if res:
                        found.append({"url": brain.getURL(), "title": brain.Title})
            i += 1
        logger.info("### END ###")
        logger.info('### {} items with block "{}" ###'.format(len(found), block_type))

        self.results = {"found": found}
        return super().__call__()

    def has_block(self, data, block_type, text):
        blocks = deepcopy(data)
        if isinstance(data, str):
            try:
                blocks = json.loads(data)
            except Exception:
                return False
        if not isinstance(blocks, dict):
            return False
        if "blocks" in blocks:
            blocks = blocks["blocks"]

        for block in blocks.values():
            if not isinstance(block, dict):
                continue
            if block_type:
                if block.get("@type", "") == block_type:
                    if text:
                        if text in json.dumps(block):
                            return True
                    else:
                        return True
            else:
                if text:
                    if text in json.dumps(block):
                        return True
        return False

    def block_types(self):
        return sorted(BLOCKS, key=lambda x: x["title"])
