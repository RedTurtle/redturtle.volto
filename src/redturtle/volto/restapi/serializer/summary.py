# -*- coding: utf-8 -*-
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


EMPTY_DATES = [
    "1969-12-30T23:00:00+00:00",
    "2499-12-30T23:00:00+00:00",
    "2499-12-31T00:00:00+00:00",
    "2100-12-31T00:00:00",
    "2100-12-31T00:00:00+00:00",
]

EMPTY_STRINGS = ["None"]


@implementer(ISerializeToJsonSummary)
@adapter(Interface, IRedturtleVoltoLayer)
class DefaultJSONSummarySerializer(BaseSerializer):
    def get_image_scales(self, data):
        """
        this is a backward compatibility for old volto templates that need
        a full image scales object
        """
        query = self.request.form
        if not query:
            # maybe its a POST request
            query = json_body(self.request)
        metadata_fields = query.get("metadata_fields", [])

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

    def __call__(self):
        data = super().__call__()

        # return empty values if dates are not set:
        for k, v in data.items():
            if v in EMPTY_DATES:
                data[k] = None
            if v in EMPTY_STRINGS and k not in ["ExpirationDate", "EffectiveDate"]:
                # this is a Volto compatibility
                data[k] = None
        scales = self.get_image_scales(data)
        if scales:
            data["image"] = {"scales": scales}
        return data
