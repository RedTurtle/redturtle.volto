# -*- coding: utf-8 -*-
from plone.restapi.behaviors import IBlocks
from plone.restapi.interfaces import IBlockFieldSerializationTransformer
from plone.restapi.serializer.blocks import uid_to_url
from redturtle.volto.interfaces import IRedturtleVoltoLayer
from zope.component import adapter
from zope.interface import implementer
from copy import deepcopy

EXCLUDE_KEYS = ["@type"]
EXCLUDE_TYPES = ["title", "listing"]


@implementer(IBlockFieldSerializationTransformer)
@adapter(IBlocks, IRedturtleVoltoLayer)
class GenericResolveUIDSerializer(object):
    """
    Generic deserializer: parse all block data and try to convert uids into
    proper urls.
    This potentially handle all text fields and complex blocks.
    """

    order = 200  # after standard ones
    block_type = None

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, value):
        new_value = deepcopy(value)
        self.resolve_uids(block=new_value)
        return new_value

    def resolve_uids(self, block):
        if block.get("@type", "") in EXCLUDE_TYPES:
            return
        for key, val in block.items():
            if not val:
                continue
            if key in EXCLUDE_KEYS:
                continue
            if isinstance(val, str):
                block[key] = uid_to_url(val)
            elif isinstance(val, list):
                for i in val:
                    self.resolve_uids(block=i)
            elif isinstance(val, dict):
                if "entityMap" not in val.keys():
                    self.resolve_uids(block=val)
                else:
                    entity_map = val.get("entityMap", {})
                    for entity_map in entity_map.values():
                        url = entity_map["data"].get("url", "").strip("/")
                        new = uid_to_url(url)
                        entity_map["data"]["url"] = new
