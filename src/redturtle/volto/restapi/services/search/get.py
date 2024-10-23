# -*- coding: utf-8 -*-
from plone import api
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.search.handler import SearchHandler as OriginalHandler
from plone.restapi.search.utils import unflatten_dotted_dict
from plone.restapi.services import Service
from redturtle.volto import logger
from redturtle.volto.config import MAX_LIMIT
from redturtle.volto.interfaces import IRedTurtleVoltoSettings
from zope.component import getMultiAdapter


# search for 'ranking' in 'SearchableText' and rank very high
# when the term is in 'Subject' and high when it is in 'Title'.
# print the id and the normalized rank
try:
    from Products.AdvancedQuery import And
    from Products.AdvancedQuery import Eq
    from Products.AdvancedQuery import In
    from Products.AdvancedQuery import Or
    from Products.AdvancedQuery import RankByQueries_Sum

    HAS_ADVANCEDQUERY = True
except ImportError:
    HAS_ADVANCEDQUERY = False


class AdvancedQueryParsingException(Exception):
    pass


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
            try:
                queries = self.get_advanced_search_query(query=query)
            except AdvancedQueryParsingException:
                query = self.request.form.copy()
                query = unflatten_dotted_dict(query)
                return super(SearchHandler, self).search(query)

            # TODO: mettere i parametri di ranking in registry
            # XXX: il default sul subject ha senso ? (probabilmente no), rivedere eventualmente anche i test
            term = query.get("SearchableText")
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
        return super().search(query)

    def get_advanced_search_query(self, query):
        if "use_site_search_settings" in query:
            del query["use_site_search_settings"]
            query = self.filter_query(query)

        self._constrain_query_by_path(query)
        query = self._parse_query(query)
        queries = []
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
            elif index_type is None:
                # skip, non-existent index
                continue
            else:
                logger.warning(
                    f"Unsupported query parameter: {key} {index_type} {value}. Fall back to the standard query."
                )
                raise (AdvancedQueryParsingException)
        return queries

    def _parse_query(self, query):
        """
        set a max limit for anonymous calls
        """
        query = super()._parse_query(query)
        if api.user.is_anonymous():
            for idx in ["sort_limit", "b_size"]:
                if idx not in query:
                    continue
                value = query.get(idx, MAX_LIMIT)
                if value <= 0:
                    logger.warning(
                        '[wrong query] {} is wrong: "{}". Set to default ({}).'.format(
                            idx, query, MAX_LIMIT
                        )
                    )
                    query[idx] = MAX_LIMIT

                if value > MAX_LIMIT:
                    logger.warning(
                        '[wrong query] {} is too high: "{}". Set to default ({}).'.format(
                            idx, query, MAX_LIMIT
                        )
                    )
                    query[idx] = MAX_LIMIT
        return query


class SearchGet(Service):
    def reply(self):
        query = self.request.form.copy()
        query = unflatten_dotted_dict(query)
        return SearchHandler(self.context, self.request).search(query)
