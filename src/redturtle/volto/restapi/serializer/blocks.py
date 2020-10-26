# -*- coding: utf-8 -*-
from copy import deepcopy
from plone import api
from plone.restapi.behaviors import IBlocks
from plone.restapi.interfaces import IBlockFieldSerializationTransformer
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.serializer.blocks import uid_to_url
from redturtle.volto.interfaces import IRedturtleVoltoLayer
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.globalrequest import getRequest
from zope.interface import implementer

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
        return self.resolve_uids(block=new_value)

    def resolve_uids(self, block):
        if isinstance(block, str):
            return uid_to_url(block)
        if block.get("@type", "") in EXCLUDE_TYPES:
            return block
        if isinstance(block, dict) and "UID" in block.keys():
            # expand internal relations
            item = api.content.get(UID=block["UID"])
            if item:
                return getMultiAdapter(
                    (item, getRequest()), ISerializeToJson
                )()
        for key, val in block.items():
            if not val:
                continue
            if key in EXCLUDE_KEYS:
                continue
            if isinstance(val, str):
                block[key] = uid_to_url(val)
            elif isinstance(val, list):
                block[key] = [self.resolve_uids(block=x) for x in val]
            elif isinstance(val, dict):
                if "entityMap" in val.keys():
                    entity_map = val.get("entityMap", {})
                    for entity_map in entity_map.values():
                        url = entity_map["data"].get("url", "").strip("/")
                        new = uid_to_url(url)
                        entity_map["data"]["url"] = new
                else:
                    block[key] = self.resolve_uids(block=val)
        return block
