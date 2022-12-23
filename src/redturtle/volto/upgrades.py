# -*- coding: utf-8 -*-
from Acquisition import aq_base
from copy import deepcopy
from plone import api
from plone.dexterity.utils import iterSchemata
from zope.schema import getFields
from plone.app.upgrade.utils import installOrReinstallProduct
from plone.restapi.behaviors import IBlocks
from uuid import uuid4

import logging
import json

try:
    from collective.volto.blocksfield.field import BlocksField

    HAS_BLOCKSFIELD = True
except ImportError:
    HAS_BLOCKSFIELD = False

logger = logging.getLogger(__name__)

DEFAULT_PROFILE = "profile-redturtle.volto:default"


def update_profile(context, profile, run_dependencies=True):
    context.runImportStepFromProfile(DEFAULT_PROFILE, profile, run_dependencies)


def update_types(context):
    update_profile(context, "typeinfo")


def update_rolemap(context):
    update_profile(context, "rolemap")


def update_registry(context):
    update_profile(context, "plone.app.registry", run_dependencies=False)


def update_controlpanel(context):
    update_profile(context, "controlpanel")


def update_catalog(context):
    update_profile(context, "catalog")


def to_1003(context):
    """
    removed the method that updated robots.txt, so this upgrade-step does nothing
    """


def to_1004(context):
    """ """
    brains = api.content.find(portal_type="Event")
    logger.info("Reindexing {} Events".format(len(brains)))

    for brain in brains:
        event = brain.getObject()
        event.reindexObject(idxs=["start", "end"])


def to_1005(context):
    context.runImportStepFromProfile(
        "profile-plone.app.caching:default", "plone.app.registry", False
    )
    context.runImportStepFromProfile(
        "profile-plone.app.caching:with-caching-proxy",
        "plone.app.registry",
        False,
    )


def to_volto13(context):  # noqa: C901
    # convert listing blocks with new standard

    logger.info("### START CONVERSION TO VOLTO 13 ###")

    def fix_listing(blocks, url):
        for block in blocks.values():
            if block.get("@type", "") != "listing":
                continue
            # fix template
            if block.get("template", False) and not block.get("variation", False):
                block["variation"] = block["template"]
                del block["template"]
                logger.info("- {}".format(url))
            if block.get("template", False) and block.get("variation", False):
                del block["template"]
                logger.info("- {}".format(url))

            # Migrate to internal structure
            if not block.get("querystring", False):
                # Creates if it is not created
                block["querystring"] = {}
            if block.get("query", False) or block.get("query") == []:
                if not block["querystring"].get("query", []):
                    # first time.
                    # there is a bug in volto that re-creates block['query']
                    block["querystring"]["query"] = block["query"]
                del block["query"]
            if block.get("sort_on", False):
                block["querystring"]["sort_on"] = block["sort_on"]
                del block["sort_on"]
            if block.get("sort_order", False):
                block["querystring"]["sort_order"] = block["sort_order"]
                if isinstance(block["sort_order"], bool):
                    block["querystring"]["sort_order"] = (
                        "descending" if block["sort_order"] else "ascending"
                    )
                else:
                    block["querystring"]["sort_order"] = block["sort_order"]
                block["querystring"]["sort_order_boolean"] = (
                    True
                    if block["sort_order"] == "descending"
                    or block["sort_order"]  # noqa
                    else False
                )
                del block["sort_order"]
            if block.get("limit", False):
                block["querystring"]["limit"] = block["limit"]
                del block["limit"]
            if block.get("batch_size", False):
                block["querystring"]["batch_size"] = block["batch_size"]
                del block["batch_size"]
            if block.get("b_size", False):
                block["querystring"]["b_size"] = block["b_size"]
                del block["b_size"]
            if block.get("depth", False):
                block["querystring"]["depth"] = block["depth"]
                del block["depth"]

            # batch_size to b_size, idempotent
            if block["querystring"].get("batch_size", False):
                block["querystring"]["b_size"] = block["querystring"]["batch_size"]
                del block["querystring"]["batch_size"]

            # fix linkMore
            if "linkMore" in block:
                block["linkTitle"] = block["linkMore"].get("title", "")
                href = block["linkMore"].get("href", "")
                item = api.content.get(href)
                if item:
                    block["linkHref"] = [
                        {
                            "@id": href,
                            "Description": item.Description(),
                            "Title": item.Title(),
                            "title": item.Title(),
                        }
                    ]
                else:
                    block["linkHref"] = [{"@id": href, "title": href}]
                del block["linkMore"]
                logger.info(" - [LINKMORE] {}".format(url))

    # fix root
    portal = api.portal.get()

    portal_blocks = getattr(portal, "blocks", "")
    if portal_blocks:
        portal_blocks = json.loads(portal_blocks)
        fix_listing(portal_blocks, portal.absolute_url())
        portal.blocks = json.dumps(portal_blocks)

    # fix blocks in contents
    pc = api.portal.get_tool(name="portal_catalog")
    brains = pc()
    tot = len(brains)
    i = 0
    for brain in brains:
        i += 1
        if i % 1000 == 0:
            logger.info("Progress: {}/{}".format(i, tot))
        item = aq_base(brain.getObject())
        if getattr(item, "blocks", {}):
            blocks = deepcopy(item.blocks)
            if blocks:
                fix_listing(blocks, brain.getURL())
                item.blocks = blocks
        for schema in iterSchemata(item):
            # fix blocks in blocksfields
            for name, field in getFields(schema).items():
                if name == "blocks":
                    blocks = deepcopy(item.blocks)
                    if blocks:
                        fix_listing(blocks, brain.getURL())
                        item.blocks = blocks
                else:
                    if not HAS_BLOCKSFIELD:
                        # blocks are only in blocks field
                        continue
                    if isinstance(field, BlocksField):
                        value = deepcopy(field.get(item))
                        if not value:
                            continue
                        if isinstance(value, str):
                            if value == "":
                                setattr(
                                    item,
                                    name,
                                    {"blocks": {}, "blocks_layout": {"items": []}},
                                )
                                continue
                        try:
                            blocks = value.get("blocks", {})
                        except AttributeError:
                            logger.warning(
                                "[RICHTEXT] - {} (not converted)".format(brain.getURL())
                            )
                        if blocks:
                            fix_listing(blocks, brain.getURL())
                            setattr(item, name, value)


def to_volto13_bis(context):  # noqa: C901
    # convert listing blocks with new standard

    logger.info("### START FIXING B_SIZE ###")

    def fix_listing(blocks, url):
        for block in blocks.values():
            if block.get("@type", "") != "listing":
                continue
            # fix template
            if not block.get("b_size", False):
                continue
            if block.get("b_size", False):
                block["querystring"]["b_size"] = block["b_size"]
                del block["b_size"]
            logger.info("- {}".format(url))

    # fix root
    portal = api.portal.get()

    portal_blocks = getattr(portal, "blocks", "")
    if portal_blocks:
        portal_blocks = json.loads(portal_blocks)
        fix_listing(portal_blocks, portal.absolute_url())
        portal.blocks = json.dumps(portal_blocks)

    # fix blocks in contents
    pc = api.portal.get_tool(name="portal_catalog")
    brains = pc()
    tot = len(brains)
    i = 0
    for brain in brains:
        i += 1
        if i % 1000 == 0:
            logger.info("Progress: {}/{}".format(i, tot))
        item = aq_base(brain.getObject())
        if getattr(item, "blocks", {}):
            blocks = deepcopy(item.blocks)
            if blocks:
                fix_listing(blocks, brain.getURL())
                item.blocks = blocks
        for schema in iterSchemata(item):
            # fix blocks in blocksfields
            for name, field in getFields(schema).items():
                if name == "blocks":
                    blocks = deepcopy(item.blocks)
                    if blocks:
                        fix_listing(blocks, brain.getURL())
                        item.blocks = blocks
                else:
                    if not HAS_BLOCKSFIELD:
                        # blocks are only in blocks field
                        continue
                    if isinstance(field, BlocksField):
                        value = deepcopy(field.get(item))
                        if not value:
                            continue
                        if isinstance(value, str):
                            if value == "":
                                setattr(
                                    item,
                                    name,
                                    {"blocks": {}, "blocks_layout": {"items": []}},
                                )
                                continue
                        try:
                            blocks = value.get("blocks", {})
                        except AttributeError:
                            logger.warning(
                                "[RICHTEXT] - {} (not converted)".format(brain.getURL())
                            )
                        if blocks:
                            fix_listing(blocks, brain.getURL())
                            setattr(item, name, value)


def to_1300(context):
    logger.info("Reindexing SearchableText")
    pc = api.portal.get_tool(name="portal_catalog")
    pc.reindexIndex("SearchableText", context.REQUEST)


def to_1400(context):
    logger.info("Disable ramcache for terse caching")
    api.portal.set_registry_record(
        "plone.app.caching.terseCaching.plone.content.dynamic.ramCache", False
    )


def to_2000(context):
    portal_types = api.portal.get_tool(name="portal_types")
    document_behaviors = list(portal_types["Document"].behaviors) + [
        "volto.preview_image"
    ]

    old_images = api.portal.get_registry_record(name="plone.allowed_sizes")
    installOrReinstallProduct(api.portal.get(), "plone.volto")

    # adjust behaviors
    portal_types["Document"].behaviors = tuple(document_behaviors)

    # adjust image scales
    new_images = api.portal.get_registry_record(name="plone.allowed_sizes")
    new_keys = [x.split(" ")[0] for x in new_images]
    for old_value in old_images:
        miniature = old_value.split(" ")[0]
        if miniature not in new_keys:
            new_images.append(old_value)

    api.portal.set_registry_record("plone.allowed_sizes", new_images)


def to_2100(context):  # noqa: C901
    logger.info("## Reindex pages with table blocks ##")

    def has_table_block(blocks):
        for block in blocks.values():
            if block.get("@type", "") == "table":
                return True
        return False

    pc = api.portal.get_tool(name="portal_catalog")
    brains = pc()
    tot = len(brains)
    i = 0
    items_reindexed = []
    for brain in brains:
        i += 1
        if i % 1000 == 0:
            logger.info("Progress: {}/{}".format(i, tot))
        item_obj = brain.getObject()
        item = aq_base(item_obj)
        if getattr(item, "blocks", {}):
            if has_table_block(item.blocks):
                items_reindexed.append(brain.getPath())
                item_obj.reindexObject(idxs=["SearchableText"])
        for schema in iterSchemata(item):
            # fix blocks in blocksfields
            for name, field in getFields(schema).items():
                if name == "blocks":
                    blocks = getattr(item, "blocks", {})
                    if has_table_block(blocks):
                        items_reindexed.append(brain.getPath())
                        item_obj.reindexObject(idxs=["SearchableText"])
                else:
                    if not HAS_BLOCKSFIELD:
                        # blocks are only in blocks field
                        continue
                    if isinstance(field, BlocksField):
                        value = field.get(item)
                        if not value:
                            continue
                        if isinstance(value, str):
                            continue
                        blocks = value.get("blocks", {})
                        if has_table_block(blocks):
                            items_reindexed.append(brain.getPath())
                            item_obj.reindexObject(idxs=["SearchableText"])

    logger.info("Reindexed {} items".format(len(items_reindexed)))
    for path in items_reindexed:
        logger.info("- {}".format(path))


def to_2200(context):  # noqa: C901
    logger.info("## Add default blocks ##")

    pc = api.portal.get_tool(name="portal_catalog")
    brains = pc(object_provides=IBlocks.__identifier__)
    tot = len(brains)
    i = 0
    items_fixed = []
    for brain in brains:
        i += 1
        if i % 500 == 0:
            logger.info("Progress: {}/{}".format(i, tot))
        item_obj = brain.getObject()
        item = aq_base(item_obj)
        blocks = getattr(item, "blocks", {})
        if not blocks or blocks == {}:
            title_uuid = str(uuid4())
            item.blocks = {title_uuid: {"@type": "title"}}
            item.blocks_layout = {"items": [title_uuid]}
            items_fixed.append(brain.getPath())
    logger.info("Fixed {} items".format(len(items_fixed)))


def to_3000(context):
    logger.info("Reindexing image_field")
    catalog = api.portal.get_tool("portal_catalog")

    brains = api.content.find(
        object_provides="plone.app.contenttypes.behaviors.leadimage.ILeadImage"
    )
    tot = len(brains)
    i = 0
    for brain in brains:
        i += 1
        if i % 500 == 0:
            logger.info("Progress: {}/{}".format(i, tot))
        obj = brain.getObject()
        catalog.catalog_object(obj)


def to_3100(context):
    logger.info("Reindexing Events")
    update_catalog(context)
    catalog = api.portal.get_tool("portal_catalog")

    brains = api.content.find(portal_type="Event")
    tot = len(brains)
    i = 0
    for brain in brains:
        i += 1
        if i % 500 == 0:
            logger.info("Progress: {}/{}".format(i, tot))
        obj = brain.getObject()
        catalog.catalog_object(obj)


def to_4000(context):
    portal_types = api.portal.get_tool(name="portal_types")
    fti = portal_types["Folder"]
    fti.global_allow = True

    for ptype in ["Event", "News Item"]:
        fti = portal_types[ptype]
        fti.filter_content_types = True
        fti.allowed_content_types = (
            "Document",
            "Image",
            "File",
            "Link",
        )


def to_4100(context):
    logger.info("Remove etags from p.a.caching terseCaching config")
    api.portal.set_registry_record(
        "plone.app.caching.terseCaching.plone.content.dynamic.etags", ()
    )
