# -*- coding: utf-8 -*-
from datetime import datetime
from DateTime import DateTime
from plone import api
from plone.app.event.base import get_events
from plone.app.querystring import queryparser
from plone.restapi.batching import HypermediaBatch
from plone.restapi.bbb import IPloneSiteRoot
from plone.restapi.deserializer import json_body
from plone.restapi.exceptions import DeserializationError
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.services import Service
from plone.restapi.services.querystringsearch.get import (
    QuerystringSearch as BaseQuerystringSearch,
)
from plone.restapi.services.querystringsearch.get import SUPPORT_NOT_UUID_QUERIES
from redturtle.volto.config import MAX_LIMIT
from urllib import parse
from zExceptions import BadRequest
from zope.component import getMultiAdapter

import logging


logger = logging.getLogger(__name__)


class QuerystringSearch(BaseQuerystringSearch):
    def __call__(self):
        try:
            data = json_body(self.request)
        except DeserializationError as err:
            raise BadRequest(str(err))

        query = data.get("query", None)

        if self.is_event_search(query=query):
            return self.reply_events()

        try:
            b_start = int(data.get("b_start", 0))
        except ValueError:
            self.request.response.setStatus(400)
            return dict(error=dict(type="BadRequest", message="Invalid b_start"))
        try:
            b_size = int(data.get("b_size", 25))
        except ValueError:
            self.request.response.setStatus(400)
            return dict(error=dict(type="BadRequest", message="Invalid b_size"))
        sort_on = data.get("sort_on", None)
        sort_order = data.get("sort_order", None)

        query = self.cleanup_query(query=query, b_size=b_size)

        # LIMIT PATCH
        if not query:
            self.request.response.setStatus(400)
            return dict(error=dict(type="BadRequest", message="No query supplied"))
        limit = self.get_limit(data=data)
        # END OF LIMIT PATCH

        fullobjects = bool(data.get("fullobjects", False))

        if sort_order:
            sort_order = "descending" if sort_order == "descending" else "ascending"

        querybuilder = getMultiAdapter(
            (self.context, self.request), name="querybuilderresults"
        )

        querybuilder_parameters = dict(
            query=query,
            brains=True,
            b_start=b_start,
            b_size=b_size,
            sort_on=sort_on,
            sort_order=sort_order,
            limit=limit,
        )

        # Exclude "self" content item from the results when ZCatalog supports NOT UUID
        # queries and it is called on a content object.
        if not IPloneSiteRoot.providedBy(self.context) and SUPPORT_NOT_UUID_QUERIES:
            querybuilder_parameters.update(
                dict(custom_query={"UID": {"not": self.context.UID()}})
            )

        try:
            results = querybuilder(**querybuilder_parameters)
        except KeyError:
            # This can happen if the query has an invalid operation,
            # but plone.app.querystring doesn't raise an exception
            # with specific info.
            self.request.response.setStatus(400)
            return dict(error=dict(type="BadRequest", message="Invalid query"))

        results = getMultiAdapter((results, self.request), ISerializeToJson)(
            fullobjects=fullobjects
        )
        return results

    def cleanup_query(self, query, b_size):
        """
        If b_size == 1 and there is an absolutePath in query that points to a non
        existing content, reeturn empty query.
        This is the case where absolutePath points to an UID that is not present on the site.
        A call with b_size == 1 usually is made in objectbrowser to draw the reference, but with a
        wrong UID, Plone by default return all site contents and the first one will be returned.
        If you then save the blocks, you'll have that random content as new absolutePath value.
        """
        if b_size != 1:
            return query
        fixed_query = []
        for criteria in query:
            index = criteria.get("i", "")
            operation = criteria.get("o", "")
            if (
                index == "path"
                and operation  # noqa
                == "plone.app.querystring.operation.string.absolutePath"  # noqa
            ):
                criteria_value = criteria.get("v", "").split("::")
                value = criteria_value[0]

                if "/" not in value:
                    # It must be a UID
                    item = api.content.get(UID=value)
                    if not item:
                        continue
                else:
                    item = api.content.get(value)
                    if not item:
                        continue
            fixed_query.append(criteria)
        return fixed_query

    def get_limit(self, data):
        """
        If limit is <= 0 or higher than MAX_LIMIT, set it to MAX_LIMIT
        """
        is_anon = api.user.is_anonymous()
        default_value = is_anon and MAX_LIMIT or max(1000, MAX_LIMIT)
        if "limit" not in data:
            return default_value
        try:
            limit = int(data.get("limit", default_value))
        except ValueError as exc:
            raise BadRequest("Invalid limit") from exc

        if limit <= 0:
            del data["limit"]
            limit = default_value
        if limit > default_value:
            logger.warning(
                '[wrong query] limit is too high: "{}". Set to default ({}).'.format(
                    data["query"], default_value
                )
            )
            limit = default_value
        return limit

    def is_event_search(self, query):
        """
        Check if we need to perform a custom search with p.a.events method
        """
        if not query:
            return False

        indexes = [x["i"] for x in query]

        portal_type_check = False
        indexes_check = "start" in indexes

        for param in query:
            i = param.get("i", "")
            v = param.get("v", [])
            if i == "portal_type" and v == ["Event"]:
                portal_type_check = True
        return portal_type_check and indexes_check

    def generate_query_for_events(self):
        data = json_body(self.request)
        parsed_query = queryparser.parseFormquery(
            context=self.context, formquery=data["query"]
        )
        fullobjects = data.get("fullobjects", False)
        b_size = data.get("b_size", None)
        b_start = data.get("b_start", 0)
        query = {k: v for k, v in parsed_query.items() if k not in ["start", "end"]}
        limit = int(self.get_limit(data=data))
        sort = "start"
        sort_reverse = False
        start, end = self.parse_event_dates(parsed_query)
        if data.get("sort_on", ""):
            sort = data["sort_on"]
        if data.get("sort_order", ""):
            sort_reverse = data["sort_order"] == "descending" and True or False
        return (
            start,
            end,
            fullobjects,
            b_size,
            b_start,
            query,
            sort_reverse,
            sort,
            limit,
        )

    def parse_event_dates(self, parsed_query):
        start = None
        end = None

        query_start = parsed_query.get("start", {})
        query_end = parsed_query.get("end", {})
        if not query_start and not query_end:
            return start, end

        if query_start:
            range = query_start.get("range", "")
            value = query_start.get("query", "")

            if not query_end and isinstance(value, list) and range == "minmax":
                start = self.get_datetime_value(value[0])
                end = self.get_datetime_value(value[1])
                return start, end
            start = self.get_datetime_value(value)
        if query_end:
            range = query_end.get("range", "")
            value = query_end.get("query", "")
            if not query_start and isinstance(value, list) and range == "minmax":
                start = self.get_datetime_value(value[0])
                end = self.get_datetime_value(value[1])
                return start, end
            dt_value = self.get_datetime_value(value)
            if range == "min":
                start = dt_value
            elif range == "max":
                end = dt_value

        return start, end

    def get_datetime_value(self, value):
        if isinstance(value, DateTime):
            return value.utcdatetime()
        return datetime.fromisoformat(value)

    def reply_events(self):
        """
        use plone.app.event query for a better recurrences management
        """
        (
            start,
            end,
            fullobjects,
            b_size,
            b_start,
            query,
            sort_reverse,
            sort,
            limit,
        ) = self.generate_query_for_events()
        brains = get_events(
            start=start,
            end=end,
            context=self.context,
            sort=sort,
            sort_reverse=sort_reverse,
            limit=limit,
            **query,
        )
        batch = HypermediaBatch(self.request, brains)
        results = {}
        results["@id"] = batch.canonical_url
        results["items_total"] = batch.items_total
        links = batch.links
        if links:
            results["batching"] = links

        results["items"] = []
        for brain in batch:
            result = None
            if fullobjects:
                try:
                    result = getMultiAdapter(
                        (brain.getObject(), self.request), ISerializeToJson
                    )(include_items=False)
                except KeyError:
                    # Guard in case the brain returned refers to an object that
                    # doesn't exists because it failed to uncatalog itself or
                    # the catalog has stale cataloged objects for some reason
                    logger.warning(
                        "Brain getObject error: {} doesn't exist anymore".format(  # noqa
                            brain.getPath()
                        )
                    )
            else:
                result = getMultiAdapter(
                    (brain, self.request), ISerializeToJsonSummary
                )()
            if result:
                results["items"].append(result)

        return results


class QuerystringSearchPost(Service):
    """Copied from plone.restapi == 8.42.0"""

    def reply(self):
        querystring_search = QuerystringSearch(self.context, self.request)
        return querystring_search()


class QuerystringSearchGet(Service):
    """Copied from plone.restapi == 8.42.0"""

    def reply(self):
        # We need to copy the JSON query parameters from the querystring
        # into the request body, because that's where other code expects to find them
        self.request["BODY"] = parse.unquote(
            self.request.form.get("query", "{}")
        ).encode(self.request.charset)
        # unset the get parameters
        self.request.form = {}
        querystring_search = QuerystringSearch(self.context, self.request)
        return querystring_search()
