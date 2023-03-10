# -*- coding: utf-8 -*-
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.search.handler import SearchHandler as OriginalHandler
from plone.restapi.search.utils import unflatten_dotted_dict
from plone.restapi.services import Service
from zope.component import getMultiAdapter

# search for 'ranking' in 'SearchableText' and rank very high
# when the term is in 'Subject' and high when it is in 'Title'.
# print the id and the normalized rank
try:
    from Products.AdvancedQuery import RankByQueries_Sum
    from Products.AdvancedQuery import Eq
    # from Products.AdvancedQuery import In

    HAS_ADVANCEDQUERY = True
except ImportError:
    HAS_ADVANCEDQUERY = False


# custom search handler


class SearchHandler(OriginalHandler):
    def is_advanced_query(self, query):
        simple_query = query.get("SimpleQuery", None)
        if simple_query:
            return False
        # TODO: aggiungere un parametro in registry per abilitare/disabilitare
        if HAS_ADVANCEDQUERY and "SearchableText" in query:
            return True
        return False

    # XXX: sarebbe meglio una monkeypatch a catalog.searchResults ? eviterebbe di
    #      ripotare tutto il codice di search qui
    def search(self, query=None):
        query = self.request.form.copy()
        query = unflatten_dotted_dict(query)
        if self.is_advanced_query(query):
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
            term = query.pop("SearchableText")
            # TODO: mettere i parametri di ranking in registry
            rs = RankByQueries_Sum(
                (Eq("Subject", term), 16),
                (Eq("Title", term), 8),
                (Eq("Description", term), 6),
            )
            print(self.catalog.searchResults)
            lazy_resultset = self.catalog.evalAdvancedQuery(
                Eq("SearchableText", term), (rs,), **query
            )
            # DEBUG: TODO: potrebbe essere utile mettere i ranking nella risposta ?
            # norm = 1 + rs.getQueryValueSum()
            # print([(r.getId, (1 + r.data_record_score_[0]) / norm) for r in lazy_resultset])
            results = getMultiAdapter((lazy_resultset, self.request), ISerializeToJson)(
                fullobjects=fullobjects
            )

            return results
        else:
            return super(SearchHandler, self).search(query)


class SearchGet(Service):
    def reply(self):
        query = self.request.form.copy()
        query = unflatten_dotted_dict(query)
        return SearchHandler(self.context, self.request).search(query)
