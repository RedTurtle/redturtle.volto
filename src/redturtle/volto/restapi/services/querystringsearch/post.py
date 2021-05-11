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

import logging

logger = logging.getLogger(__name__)


class RTQuerystringSearchPost(QuerystringSearchPost):
    """
    Perform a custom search if we are searching events
    """

    def reply(self):
        query = json_body(self.request).get("query", [])
        for param in query:
            i = param.get("i", "")
            v = param.get("v", [])
            if i == "portal_type" and v == ["Event"]:
                # do a custom search
                return self.reply_events()
        return super(RTQuerystringSearchPost, self).reply()

    def generate_query_for_events(self):
        data = json_body(self.request)
        parsed_query = queryparser.parseFormquery(
            context=self.context, formquery=data["query"]
        )
        fullobjects = data.get("fullobjects", False)
        b_size = data.get("b_size", None)
        b_start = data.get("b_start", 0)
        query = {
            k: v for k, v in parsed_query.items() if k not in ["start", "end"]
        }
        limit = int(data.get("limit", 1000))
        sort = "start"
        sort_reverse = False
        start = None
        end = None
        if parsed_query.get("start", ""):
            start = datetime.fromisoformat(parsed_query["start"]["query"])
        if parsed_query.get("end", ""):
            end = datetime.fromisoformat(parsed_query["end"]["query"])
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
