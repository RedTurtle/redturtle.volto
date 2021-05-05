# -*- coding: utf-8 -*-
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.search.handler import SearchHandler as OriginalHandler
from plone.restapi.search.utils import unflatten_dotted_dict
from plone.restapi.services import Service
from zope.component import getMultiAdapter


class SearchHandler(OriginalHandler):
    def search(self, query=None):
        if query is None:
            query = {}
        if "fullobjects" in query:
            fullobjects = True
            del query["fullobjects"]
        else:
            fullobjects = False

        if "use_site_search_settings" in query:
            del query["use_site_search_settings"]
            query = self.filter_query(query)

        self._constrain_query_by_path(query)
        query = self._parse_query(query)
        # se non passiamo i parametri con **, non viene controllato bene
        # il permesso di vedere i contenuti scaduti quando si passa un path
        lazy_resultset = self.catalog.searchResults(**query)
        results = getMultiAdapter(
            (lazy_resultset, self.request), ISerializeToJson
        )(fullobjects=fullobjects)

        return results


class SearchGet(Service):
    def reply(self):
        query = self.request.form.copy()
        query = unflatten_dotted_dict(query)
        return SearchHandler(self.context, self.request).search(query)
