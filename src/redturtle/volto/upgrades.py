# -*- coding: utf-8 -*-
from Acquisition import aq_base
from copy import deepcopy
from plone import api
from plone.dexterity.utils import iterSchemata
from zope.schema import getFields

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
