# -*- coding: utf-8 -*-
from plone import api
from plone.restapi.services import Service


class SitemapGet(Service):
    def reply(self):
        return {"depth": api.portal.get_registry_record("plone.sitemap_depth")}
