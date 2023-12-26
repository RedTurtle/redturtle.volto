# -*- coding: utf-8 -*-
from BTrees.OOBTree import OOBTree
from plone.app.layout.sitemap.sitemap import SiteMapView as LayoutSiteMapView
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IPloneSiteRoot
from zope.component import getUtility

import datetime


class SiteMapView(LayoutSiteMapView):
    def objects(self):
        """Returns the data to create the sitemap.

        This is a copy of the original method from plone.app.layout.sitemap.sitemap

        The only difference is that:
        * we restrict level of depth to `plone.sitemap_depth` registry setting
        * we add content modified in the last week
        """
        catalog = getToolByName(self.context, "portal_catalog")
        query = {}
        utils = getToolByName(self.context, "plone_utils")
        query["portal_type"] = utils.getUserFriendlyTypes()
        registry = getUtility(IRegistry)
        typesUseViewActionInListings = frozenset(
            registry.get("plone.types_use_view_action_in_listings", [])
        )

        is_plone_site_root = IPloneSiteRoot.providedBy(self.context)
        # if not is_plone_site_root:
        #     query["path"] = "/".join(self.context.getPhysicalPath())
        query["path"] = {
            "query": "/".join(self.context.getPhysicalPath()),
            "depth": registry.get("plone.sitemap_depth", 3),
        }

        query["is_default_page"] = True
        default_page_modified = OOBTree()
        for item in catalog.searchResults(query):
            key = item.getURL().rsplit("/", 1)[0]
            value = (item.modified.micros(), item.modified.ISO8601())
            default_page_modified[key] = value

        # The plone site root is not catalogued.
        if is_plone_site_root:
            loc = self.context.absolute_url()
            date = self.context.modified()
            # Comparison must be on GMT value
            modified = (date.micros(), date.ISO8601())
            default_modified = default_page_modified.get(loc, None)
            if default_modified is not None:
                modified = max(modified, default_modified)
            lastmod = modified[1]
            yield {
                "loc": loc,
                "lastmod": lastmod,
                # 'changefreq': 'always',
                #  hourly/daily/weekly/monthly/yearly/never
                # 'prioriy': 0.5, # 0.0 to 1.0
            }

        query["is_default_page"] = False
        for item in catalog.searchResults(query):
            loc = item.getURL()
            date = item.modified
            # Comparison must be on GMT value
            modified = (date.micros(), date.ISO8601())
            default_modified = default_page_modified.get(loc, None)
            if default_modified is not None:
                modified = max(modified, default_modified)
            lastmod = modified[1]
            if item.portal_type in typesUseViewActionInListings:
                loc += "/view"
            yield {
                "loc": loc,
                "lastmod": lastmod,
                # 'changefreq': 'always',
                #  hourly/daily/weekly/monthly/yearly/never
                # 'prioriy': 0.5, # 0.0 to 1.0
            }

        # query for last modified pages. No problem if they are already in the sitemap (?)
        query["path"]["depth"] = -1
        query["modified"] = {
            "query": datetime.datetime.now() - datetime.timedelta(days=7),
            "range": "min",
        }
        for item in catalog.searchResults(query):
            loc = item.getURL()
            date = item.modified
            # Comparison must be on GMT value
            modified = (date.micros(), date.ISO8601())
            default_modified = default_page_modified.get(loc, None)
            if default_modified is not None:
                modified = max(modified, default_modified)
            lastmod = modified[1]
            if item.portal_type in typesUseViewActionInListings:
                loc += "/view"
            yield {
                "loc": loc,
                "lastmod": lastmod,
                # 'changefreq': 'always',
                #  hourly/daily/weekly/monthly/yearly/never
                "prioriy": 1.0,
            }
