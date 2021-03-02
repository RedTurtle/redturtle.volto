# -*- coding: utf-8 -*-
from AccessControl.unauthorized import Unauthorized
from copy import deepcopy
from plone import api
from plone.restapi.behaviors import IBlocks
from plone.restapi.interfaces import IBlockFieldSerializationTransformer
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.serializer.blocks import uid_to_url
from Products.CMFPlone.interfaces import IPloneSiteRoot
from redturtle.volto.interfaces import IRedturtleVoltoLayer
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.globalrequest import getRequest
from zope.interface import implementer

EXCLUDE_KEYS = ["@type"]
EXCLUDE_TYPES = ["title", "listing"]


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
            return self.get_item_from_uid(block=block)
        for key, val in block.items():
            if not val:
                continue
            if key in EXCLUDE_KEYS:
                continue
            if isinstance(val, str):
                block[key] = uid_to_url(val)
            elif isinstance(val, list):
                new_val = []
                for x in val:
                    fixed_block = self.resolve_uids(block=x)
                    if fixed_block:
                        new_val.append(fixed_block)
                block[key] = new_val
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

    def get_item_from_uid(self, block):
        try:
            item = api.content.get(UID=block["UID"])
        except Unauthorized:
            return {}
        if item:
            if item == self.context:
                # STOP RECURSION: if we serialize the complete object, we get
                # maximum recursion depth, so serialize the object with
                # summary. If we need more infos, let's add them into summary
                # serializer
                return getMultiAdapter(
                    (item, getRequest()), ISerializeToJsonSummary
                )()
            else:
                return getMultiAdapter(
                    (item, getRequest()), ISerializeToJson
                )()
        else:
            return {}


@implementer(IBlockFieldSerializationTransformer)
@adapter(IBlocks, IRedturtleVoltoLayer)
class GenericResolveUIDSerializerContents(GenericResolveUIDSerializer):
    """ Deserializer for content-types that implements IBlocks behavior """


@implementer(IBlockFieldSerializationTransformer)
@adapter(IPloneSiteRoot, IRedturtleVoltoLayer)
class GenericResolveUIDSerializerRoot(GenericResolveUIDSerializer):
    """ Deserializer for site-root """
