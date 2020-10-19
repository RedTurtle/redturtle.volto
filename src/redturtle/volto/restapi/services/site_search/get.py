# -*- coding: utf-8 -*-
from plone import api
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.search.handler import SearchHandler as OriginalHandler
from plone.restapi.search.utils import unflatten_dotted_dict
from plone.restapi.services import Service
from zope.component import getMultiAdapter


class SearchHandler(OriginalHandler):
    def filter_types(self):
        plone_utils = api.portal.get_tool(name="plone_utils")
        return plone_utils.getUserFriendlyTypes([])

    def search(self, query=None):
        if query is None:
            query = {}
        if "fullobjects" in query:
            fullobjects = True
            del query["fullobjects"]
        else:
            fullobjects = False

        if "portal_type" not in query:
            query["portal_type"] = self.filter_types()

        self._constrain_query_by_path(query)
        query = self._parse_query(query)

        lazy_resultset = self.catalog.searchResults(query)
        results = getMultiAdapter((lazy_resultset, self.request), ISerializeToJson)(
            fullobjects=fullobjects
        )

        return results


class SearchGet(Service):
    def reply(self):
        query = self.request.form.copy()
        query = unflatten_dotted_dict(query)
        return SearchHandler(self.context, self.request).search(query)
