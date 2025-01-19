from Acquisition import aq_base
from plone import api
from plone.dexterity.utils import iterSchemata
from plone.restapi.serializer.utils import uid_to_url
from Products.Five import BrowserView
from six import StringIO
from zope.schema import getFieldsInOrder


try:
    from collective.volto.blocksfield.field import BlocksField

    HAS_BLOCKSFIELD = True
except ImportError:
    HAS_BLOCKSFIELD = False

import csv
import logging


logger = logging.getLogger(__name__)


class View(BrowserView):
    def __call__(self):
        """
        Check all contents if there are some internal links with resolveuid broken
        """
        site_id = api.portal.get().getId()
        results = self.check_links()
        self.request.response.setHeader("Content-type", "application/csv")
        self.request.response.setHeader(
            "Content-disposition", f"attachment; filename={site_id}_broken_links.csv"
        )

        sbuf = StringIO()
        writer = csv.writer(sbuf, delimiter=" ", quoting=csv.QUOTE_ALL)
        writer.writerow(["url"])
        for row in results:
            writer.writerow([row])

        res = sbuf.getvalue()
        sbuf.close()
        return res

    def check_links(self):
        """
        Check on root and all contents
        """
        res = []
        # first of all, check them on root
        res.extend(self.check_links_on_root())
        # then check on contents
        res.extend(self.check_links_on_contents())
        return res

    def check_links_on_root(self):
        """
        Check root blocks
        """
        logger.info("## Check broken links on Site Root ##")
        portal = api.portal.get()
        blocks = getattr(portal, "blocks", {})

        if self.check_blocks_broken_links(data=blocks):
            return [portal.portal_url()]
        return []

    def check_links_on_contents(self):
        """
        Iterate over site contents
        """
        logger.info("## Check broken links on Content-types ##")
        portal_catalog = api.portal.get_tool("portal_catalog")
        brains = portal_catalog()
        tot = len(brains)
        i = 0
        res = []
        for brain in brains:
            i += 1
            if (i + 1) % 200 == 0:
                logger.info(f" - Progress {i}/{tot}")
            item = brain.getObject()
            aq_base_obj = aq_base(item)

            blocks = getattr(aq_base_obj, "blocks", {})
            if blocks:
                if self.check_blocks_broken_links(data=blocks):
                    res.append(brain.getURL())
                    continue
            if not HAS_BLOCKSFIELD:
                continue
            has_broken_links = False
            for schemata in iterSchemata(aq_base_obj):
                for name, field in getFieldsInOrder(schemata):
                    if not isinstance(field, BlocksField):
                        continue
                    value = field.get(item)
                    if not value:
                        continue
                    blocks = value.get("blocks", {})
                    if self.check_blocks_broken_links(data=blocks):
                        has_broken_links = True
                        break
            if has_broken_links:
                res.append(brain.getURL())
        return res

    def check_blocks_broken_links(self, data):
        """
        Recursive method that check if there is a broken resolveuid in a block prop
        """
        if isinstance(data, str):
            if "resolveuid" not in data:
                return False
            if uid_to_url(data) == data:
                return True
            return False
        if isinstance(data, list):
            for child in data:
                res = self.check_blocks_broken_links(data=child)
                if res:
                    return True
            return False
        if isinstance(data, dict):
            for child in data.values():
                res = self.check_blocks_broken_links(data=child)
                if res:
                    return True
        return False
