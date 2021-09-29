# -*- coding: utf-8 -*-
from datetime import datetime
from plone.app.event.base import get_events
from plone.app.querystring import queryparser
from plone.restapi.batching import HypermediaBatch
from plone.restapi.deserializer import json_body
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.services.querystringsearch.get import QuerystringSearchPost
from zope.component import getMultiAdapter
from DateTime import DateTime

import logging

logger = logging.getLogger(__name__)


class RTQuerystringSearchPost(QuerystringSearchPost):
    """
    Perform a custom search if we are searching events
    """

    def reply(self):
        if self.is_event_search():
            return self.reply_events()
        return super(RTQuerystringSearchPost, self).reply()

    def is_event_search(self):
        """
        Check if we need to perform a custom search with p.a.events method
        """
        query = json_body(self.request).get("query", [])
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
        limit = int(data.get("limit", 1000))
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
