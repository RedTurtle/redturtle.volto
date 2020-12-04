# -*- coding: utf-8 -*-
from plone.restapi.services import Service
from plone import api


class SitemapGet(Service):
    def reply(self):
        return {"depth": api.portal.get_registry_record("plone.sitemap_depth")}
