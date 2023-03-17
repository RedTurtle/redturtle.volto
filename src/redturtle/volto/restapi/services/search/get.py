# -*- coding: utf-8 -*-
from plone import api
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.search.handler import SearchHandler as OriginalHandler
from plone.restapi.search.utils import unflatten_dotted_dict
from plone.restapi.services import Service
from redturtle.volto.interfaces import IRedTurtleVoltoSettings
from redturtle.volto import logger
from zope.component import getMultiAdapter

# search for 'ranking' in 'SearchableText' and rank very high
# when the term is in 'Subject' and high when it is in 'Title'.
# print the id and the normalized rank
try:
    from Products.AdvancedQuery import RankByQueries_Sum
    from Products.AdvancedQuery import Eq
    from Products.AdvancedQuery import In
    from Products.AdvancedQuery import And
    from Products.AdvancedQuery import Or

    HAS_ADVANCEDQUERY = True
except ImportError:
    HAS_ADVANCEDQUERY = False


# custom search handler


class SearchHandler(OriginalHandler):
    def get_indexes_mapping(self):
        indexes = api.portal.get_tool("portal_catalog").getIndexObjects()
        res = {}
        for index in indexes:
            index_type = index.meta_type
            res[index.getId()] = index_type
        return res

    def is_advanced_query(self, query):
        if not query:
            return False
        if query.get("sort_on", None):
            return False
        if query.get("SimpleQuery", None):
            return False
        custom_ranking_enabled = api.portal.get_registry_record(
            "enable_advanced_query_ranking", interface=IRedTurtleVoltoSettings
        )
        if HAS_ADVANCEDQUERY and "SearchableText" in query and custom_ranking_enabled:
            return True
        return False

    # XXX: sarebbe meglio una monkeypatch a catalog.searchResults ? eviterebbe di
    #      riportare tutto il codice di search qui
    def search(self, query=None):
        query = self.request.form.copy()
        query = unflatten_dotted_dict(query)
        if self.is_advanced_query(query):
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
            queries = []
            term = query.get("SearchableText")
            indexes_mapping = self.get_indexes_mapping()

            for key, value in query.items():
                index_type = indexes_mapping.get(key, None)
                if index_type == "ZCTextIndex":
                    # SearchableText, Title, Description
                    queries.append(Eq(key, value))
                elif index_type in ["KeywordIndex", "FieldIndex"]:
                    if isinstance(value, str):
                        value = [value]
                    queries.append(In(key, value))
                elif index_type == "ExtendedPathIndex":
                    if isinstance(value["query"], list):
                        queries.append(Or(*[Eq(key, p) for p in value["query"]]))
                    else:  # list/tuple ?
                        queries.append(Eq(key, value["query"]))
                elif key in ("b_start", "b_size"):
                    continue
                else:
                    logger.warning(
                        f"Unsupported query parameter: {key} {index_type} {value}. Fall back to the standard query."
                    )
                    return super(SearchHandler, self).search(query)

            # term = query.pop("SearchableText")
            # TODO: mettere i parametri di ranking in registry
            # XXX: il default sul subject ha senso ? (probabilmente no), rivedere eventualmente anche i test
            rs = RankByQueries_Sum(
                (Eq("Subject", term), 16),
                (Eq("Title", term), 8),
                (Eq("Description", term), 6),
            )

            lazy_resultset = self.catalog.evalAdvancedQuery(
                # Eq("SearchableText", term), (rs,), **query
                And(*queries),
                (rs,),
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
