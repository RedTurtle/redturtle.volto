from AccessControl import ClassSecurityInfo
from Acquisition import aq_base
from datetime import datetime
from OFS.SimpleItem import SimpleItem
from persistent.mapping import PersistentMapping
from plone import api
from plone.dexterity.utils import iterSchemata
from plone.memoize import view
from plone.restapi.interfaces import IFieldSerializer
from plone.restapi.serializer.utils import RESOLVEUID_RE
from Products.CMFCore.utils import UniqueObject
from zExceptions import NotFound
from zope.component import queryMultiAdapter
from zope.interface import implementer
from zope.interface import Interface
from zope.schema import getFieldsInOrder

import json
import logging
import re
import requests


logger = logging.getLogger(__name__)


class ILinkCheckerTool(Interface):
    """Link checker tool"""

    def clear():
        """Clear the status"""

    def check_site(ttl=3600 * 6):
        """Check the site for links"""

    def check_content(content, ttl=3600 * 6):
        """Check the content for links"""


URL_REGEX = re.compile(
    r"((?:(?:https?://)(?:(?:www\.)?(?:[\da-z\.-]+)\.(?:[a-z]{2,6}))(?::[0-9]{1,4})?)(?:[^\"\s]*)?)"
)
RESOLVEUID_REGEX = re.compile(r"^(?:|.*/)(resolve[Uu]id/[a-z0-9\-]+)")


@implementer(ILinkCheckerTool)
class LinkCheckerTool(UniqueObject, SimpleItem):
    """Tool to check links in the site"""

    id = "portal_linkchecker"
    meta_type = "Link Checker Tool"
    security = ClassSecurityInfo()

    def __init__(self):
        # link -> (last_update, status_code)
        self._external_links_status = PersistentMapping()
        # last update
        self._last_update = None
        # UUID -> (last_update, [(link1, status1), (link2, status2), ...])
        self._outgoing_links = PersistentMapping()

    @property
    def user_agent(self):
        return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
        # "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:123.0) Gecko/20100101 Firefox/123.0"

    @property
    def request(self):
        # used for view.memoize
        return api.env.getRequest()

    @property
    @view.memoize
    def portal_url(self):
        return api.portal.get().absolute_url()

    def clear(self):
        """Clear the status"""
        self._external_links_status.clear()
        self._outgoing_links.clear()
        self._last_update = None

    def check_site(self, ttl=3600 * 6):
        """Check the site for links

        :param ttl: the time to live for the external links status
        """

        def check(obj, path, **kwargs):
            logger.debug("Checking %s", path)
            self.check_content(obj, ttl)

        portal = api.portal.get()
        catalog = api.portal.get_tool("portal_catalog")
        catalog.ZopeFindAndApply(
            portal,
            search_sub=True,
            apply_func=check,
            apply_path="/".join(portal.getPhysicalPath()),
        )
        self._last_update = datetime.now()

    def check_content(self, content, ttl=3600 * 6):
        """Check the content for links

        :param content: the content to check
        :param ttl: the time to live for the external links status
        """
        uuid = content.UID()
        internal_links = []
        external_links = []
        for link in self._find_links(content):
            if self._is_internal(link):
                status = self._check_internal_link(link)
                internal_links.append((link, status))
            else:
                status = self._check_external_link(link, ttl)
                external_links.append((link, status))
        self._outgoing_links[uuid] = (datetime.now(), external_links + internal_links)

    def get_page_with_broken_links(self):
        """
        :return: iterator with items as
                 (uid, [(link1, status1), link2, status2), ...])
        """
        for uid, (_, links) in self._outgoing_links.items():
            broken_links = [item for item in links if item[1] != 200]
            if broken_links:
                yield (uid, broken_links)

    def get_rows(self, broken=True):
        """
        example usage:

            tool = api.portal.get_tool("portal_linkchecker")
            writer = csv.writer(open("broken_links.csv", "w"))
            for row in tool.get_rows():
                writer.writerow(row)
        """
        yield ["PAGE", "LINK", "STATUS"]
        for uid, (_, links) in self._outgoing_links.items():
            page = api.content.find(UID=uid, unrestricted=True)[0].getURL()
            for item in links:
                if broken and item[1] == 200:
                    continue
                yield [page, item[0], item[1]]

    def _find_links(self, item):
        """Find links in the content

        :param item: the content to check

        n.b. this is (initially) a copy of the method from redturtle.volto.browser.fix_links
        """
        links = set()
        obj = aq_base(item)
        if not hasattr(obj, "portal_type"):
            # skip Plone Site
            return []
        for schemata in iterSchemata(obj):
            for name, field in getFieldsInOrder(schemata):
                if name in ["blocks_layout"]:
                    continue
                serializer = queryMultiAdapter(
                    (field, item, self.request), IFieldSerializer
                )
                # value = getattr(obj, name, None)
                value = serializer()
                if not value:
                    continue
                elif isinstance(value, str):
                    links.update(re.findall(URL_REGEX, value))
                    links.update(re.findall(RESOLVEUID_REGEX, value))
                elif isinstance(value, dict):
                    links.update(re.findall(URL_REGEX, json.dumps(value)))
                    links.update(re.findall(RESOLVEUID_REGEX, json.dumps(value)))
                else:
                    # import pdb; pdb.set_trace()
                    continue
        return list(links)

    def _is_internal(self, link):
        """Check if the link is internal"""
        if link.startswith(self.portal_url):
            return True
        if link.startswith("http://") or link.startswith("https://"):
            return False
        return True

    @view.memoize
    def _check_internal_link(self, link):
        """Check the internal link"""
        logger.info("Checking internal link %s", link)
        link = link.replace(self.portal_url, "")
        # TODO: use subrequest or catalog ?
        match = RESOLVEUID_RE.match(link)
        if match is not None:
            uid, _ = match.groups()
            if api.content.find(UID=uid, unrestricted=True):
                return 200
            else:
                return 404
        else:
            try:
                # XXX: path is not link ....
                if api.content.get(path=link):
                    return 200
            except (NotFound, IndexError):
                return 404

        # TODO: redirection tool

        # try:
        #     from plone.subrequest import subrequest
        #     def exception_handler(response, exc):
        #         raise exc
        #     subrequest(link, exception_handler=exception_handler)
        #     return 200
        # except NotFound:
        #     return 404
        # except:
        #     raise

        return 404

    @view.memoize
    def _check_external_link(self, link, ttl=3600 * 6, timeout=1.0):
        """Check the external link"""
        logger.warning("Checking external link %s", link)

        if link in self._external_links_status:
            last_update, status = self._external_links_status[link]
            if status == 200 and (datetime.now() - last_update).total_seconds() < ttl:
                return status
        try:
            headers = {"User-Agent": self.user_agent}
            res = requests.get(link, headers=headers, timeout=timeout)
            status = res.status_code
        except requests.exceptions.RequestException:
            status = 999  # ???
        self._external_links_status[link] = (datetime.now(), status)
        return status
