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
    context.runImportStepFromProfile(
        DEFAULT_PROFILE, profile, run_dependencies
    )


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
    """
    """
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
            if block.get("@type", "") == "listing":
                if block.get("template", False) and not block.get(
                    "variation", False
                ):
                    block["variation"] = block["template"]
                    del block["template"]
                    logger.info("- {}".format(url))
                if block.get("template", False) and block.get(
                    "variation", False
                ):
                    del block["template"]
                    logger.info("- {}".format(url))

    # fix root
    portal = api.portal.get()
    portal_blocks = json.loads(portal.blocks)
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
                                    {
                                        "blocks": {},
                                        "blocks_layout": {"items": []},
                                    },
                                )
                                continue
                        blocks = value.get("blocks", {})
                        if blocks:
                            fix_listing(blocks, brain.getURL())
                            setattr(item, name, value)
