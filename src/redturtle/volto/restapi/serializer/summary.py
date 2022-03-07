# -*- coding: utf-8 -*-
from plone import api
from plone.app.contenttypes.interfaces import ILink
from plone.app.contenttypes.utils import replace_link_variables_by_paths
from plone.outputfilters.browser.resolveuid import uuidToURL
from plone.restapi.deserializer import json_body
from plone.restapi.imaging import get_scale_infos
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.serializer.summary import (
    DefaultJSONSummarySerializer as BaseSerializer,
)
from redturtle.volto.interfaces import IRedturtleVoltoLayer
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface

import re

RESOLVEUID_RE = re.compile(".*?/resolve[Uu]id/([^/]*)/?(.*)$")

EMPTY_STRINGS = ["None"]


@implementer(ISerializeToJsonSummary)
@adapter(Interface, IRedturtleVoltoLayer)
class DefaultJSONSummarySerializer(BaseSerializer):
    def get_metadata_fields(self):
        query = self.request.form
        if not query:
            # maybe its a POST request
            query = json_body(self.request)
        return query.get("metadata_fields", []) or []

    def get_image_scales(self, data):
        """
        this is a backward compatibility for old volto templates that need
        a full image scales object
        """
        metadata_fields = self.get_metadata_fields()

        if "_all" not in metadata_fields:
            return {}
        if data.get("image", None):
            # it's a fullobjects data, so we already have the infos
            return None
        if not data.get("image_field", ""):
            return None
        scales = {}
        for name, actual_width, actual_height in get_scale_infos():
            scales[name] = {
                "width": actual_width,
                "height": actual_height,
                "download": "{url}/@@images/{image_field}/{name}".format(
                    url=data["@id"], image_field=data["image_field"], name=name
                ),
            }
        return scales

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
        path = replace_link_variables_by_paths(context=self.context, url=value)
        match = RESOLVEUID_RE.match(path)
        if match:
            uid, suffix = match.groups()
            return uuidToURL(uid)
        else:
            portal = api.portal.get()
            try:
                ref_obj = portal.restrictedTraverse(path, None)
                if ref_obj:
                    return ref_obj.absolute_url()
            except Exception:
                return ""
        return ""

    def __call__(self):
        data = super().__call__()
        metadata_fields = self.get_metadata_fields()
        # return empty values if dates are not set:
        for k, v in data.items():
            if isinstance(v, str):
                if v.startswith("1969") or v.startswith("2100") or v.startswith("2499"):
                    data[k] = None
            if v in EMPTY_STRINGS and k not in ["ExpirationDate", "EffectiveDate"]:
                # this is a Volto compatibility
                data[k] = None
        scales = self.get_image_scales(data)
        if scales:
            data["image"] = {"scales": scales}
        if self.context.portal_type == "Link":
            if "_all" in metadata_fields or "remoteUrl" in metadata_fields:
                remote_url = self.get_remote_url()
                # set twice because old templates can use both
                if not remote_url:
                    data["getRemoteUrl"] = ""
                    data["remoteUrl"] = ""
                else:
                    data["remoteUrl"] = remote_url
                    data["getRemoteUrl"] = remote_url
        return data
