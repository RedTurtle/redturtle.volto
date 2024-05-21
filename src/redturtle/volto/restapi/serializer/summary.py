# -*- coding: utf-8 -*-
from plone import api
from plone.app.contenttypes.interfaces import ILink
from plone.app.contenttypes.utils import replace_link_variables_by_paths
from plone.restapi.deserializer import json_body
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.serializer.summary import (
    DefaultJSONSummarySerializer as BaseSerializer,
)
from plone.restapi.serializer.utils import uid_to_url
from redturtle.volto.interfaces import IRedturtleVoltoLayer
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface


EMPTY_STRINGS = ["None"]


@implementer(ISerializeToJsonSummary)
@adapter(Interface, IRedturtleVoltoLayer)
class DefaultJSONSummarySerializer(BaseSerializer):
    def __init__(self, context, request):
        super().__init__(context, request)
        self.force_all_metadata = False

    def metadata_fields(self):
        metadata_fields = super().metadata_fields()
        if not self.force_all_metadata:
            return metadata_fields
        fields_cache = self.request.get("_summary_fields_cache", None)
        if fields_cache is None:
            catalog = api.portal.get_tool(name="portal_catalog")
            fields_cache = set(catalog.schema()) | self.non_metadata_attributes
            self.request.set("_summary_fields_cache", fields_cache)
        return metadata_fields | fields_cache

    @property
    def show_all_metadata_fields(self):
        query = self.request.form
        if not query:
            # maybe its a POST request
            query = json_body(self.request)
        metadata_fields = query.get("metadata_fields", [])
        return "_all" in metadata_fields or self.force_all_metadata

    def get_remote_url(self):
        """
        Resolve uid and return ref absolute url
        """
        if ILink.providedBy(self.context):
            value = getattr(self.context, "remoteUrl", "")
        else:
            value = self.context.getRemoteUrl
        if not value:
            return ""
        if value.startswith("http"):
            # it isn't an internal link, so we can return it
            return value
        path = replace_link_variables_by_paths(context=self.context, url=value)

        url = uid_to_url(path)

        if url == path:
            # something wrong with the path, maybe a missing object?
            return ""
        return url

    def __call__(self, force_all_metadata=False):
        if force_all_metadata:
            self.force_all_metadata = True
        data = super().__call__()
        # return empty values if dates are not set:
        for k, v in data.items():
            if isinstance(v, str):
                if v.startswith("1969") or v.startswith("2100") or v.startswith("2499"):
                    data[k] = None
            if v in EMPTY_STRINGS and k not in ["ExpirationDate", "EffectiveDate"]:
                # this is a Volto compatibility
                data[k] = None
        if self.context.portal_type == "Link":
            remote_url = self.get_remote_url()
            # set twice because old templates can use both
            if not remote_url:
                data["getRemoteUrl"] = ""
                data["remoteUrl"] = ""
            else:
                data["remoteUrl"] = remote_url
                data["getRemoteUrl"] = remote_url
        return data
