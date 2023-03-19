# -*- coding: utf-8 -*-
from plone import api
from plone.restapi.services import Service


class SitemapSettingsGet(Service):
    def reply(self):
        return {"depth": api.portal.get_registry_record("plone.sitemap_depth")}


# TODO: add get service for sitemap xml endpoint (?)
# mimic logic from plone.app.layout.sitemap.sitemap or redturtle.volto.browser.sitemap
class SitemapGet(Service):
    def reply(self):
        return {"depth": api.portal.get_registry_record("plone.sitemap_depth")}
