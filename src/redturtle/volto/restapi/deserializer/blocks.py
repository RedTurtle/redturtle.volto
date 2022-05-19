# -*- coding: utf-8 -*-
from copy import deepcopy
from plone.restapi.behaviors import IBlocks
from plone.restapi.deserializer.blocks import path2uid
from plone.restapi.interfaces import IBlockFieldDeserializationTransformer
from Products.CMFPlone.interfaces import IPloneSiteRoot
from redturtle.volto.interfaces import IRedturtleVoltoLayer
from zope.component import adapter
from zope.interface import implementer


EXCLUDE_KEYS = ["@type", "token", "value", "@id", "query"]
EXCLUDE_TYPES = ["title", "listing", "calendar", "searchEvents"]


class GenericResolveUIDDeserializer(object):
    """
    Generic deserializer: parse all block data and try to change urls to
    resolveuids.
    This potentially handle all text fields and complex blocks.
    """

    order = 200  # after standard ones
    block_type = None

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, value):
        return self.fix_urls_in_block(block=deepcopy(value))

    def fix_urls_in_block(self, block):
        if isinstance(block, str):
            return self.get_uid_from_path(link=block)
        if block.get("@type", "") in EXCLUDE_TYPES:
            return block
        if "UID" in block.keys():
            # we store only uid, because other infos can change.
            return {"UID": block["UID"]}
        for key, val in block.items():
            if not val:
                continue
            if key in EXCLUDE_KEYS:
                continue
            if isinstance(val, str):
                block[key] = self.get_uid_from_path(link=val)
            elif isinstance(val, list):
                block[key] = [self.fix_urls_in_block(x) for x in val]
            elif isinstance(val, dict):
                if "entityMap" in val.keys():
                    entity_map = val.get("entityMap", {})
                    for entity_map in entity_map.values():
                        url = entity_map["data"].get("url", "").strip("/")
                        entity_map["data"]["url"] = self.get_uid_from_path(link=url)
                else:
                    block[key] = self.fix_urls_in_block(block=val)
        return block

    def get_uid_from_path(self, link):
        """get_uid_from_path.

        :param link:
        """
        try:
            return path2uid(context=self.context, link=link)
        except IndexError:
            # the value (link) is not a valid path
            return link


class TableResolveUIDDeserializer(object):
    """ """

    order = 210  # after standard ones
    block_type = "table"

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, block):
        for row in block.get("table", {}).get("rows", []):
            for cell in row.get("cells", []):
                for entity in cell.get("value", {}).get("entityMap", {}).values():
                    if entity.get("type") == "LINK":
                        href = entity.get("data", {}).get("url", "")
                        entity["data"]["url"] = path2uid(
                            context=self.context, link=href
                        )
        return block


@implementer(IBlockFieldDeserializationTransformer)
@adapter(IBlocks, IRedturtleVoltoLayer)
class GenericResolveUIDDeserializerContents(GenericResolveUIDDeserializer):
    """Deserializer for content-types that implements IBlocks behavior"""


@implementer(IBlockFieldDeserializationTransformer)
@adapter(IPloneSiteRoot, IRedturtleVoltoLayer)
class GenericResolveUIDDeserializerRoot(GenericResolveUIDDeserializer):
    """Deserializer for site-root"""


@implementer(IBlockFieldDeserializationTransformer)
@adapter(IBlocks, IRedturtleVoltoLayer)
class TableResolveUIDDeserializerContents(TableResolveUIDDeserializer):
    """Deserializer for content-types that implements IBlocks behavior"""


@implementer(IBlockFieldDeserializationTransformer)
@adapter(IPloneSiteRoot, IRedturtleVoltoLayer)
class TableResolveUIDDeserializerRoot(TableResolveUIDDeserializer):
    """Deserializer for site-root"""
