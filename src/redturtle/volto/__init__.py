# -*- coding: utf-8 -*-
"""Init and utils."""
from zope.i18nmessageid import MessageFactory
from plone.app.content.browser.vocabulary import PERMISSIONS
from plone.volto import upgrades
from plone.volto.upgrades import MIGRATION
from plone import api
from OFS.interfaces import IOrderedContainer

import logging

logger = logging.getLogger(__name__)


_ = MessageFactory("redturtle.volto")

PERMISSIONS["plone.app.vocabularies.Keywords"] = "View"


def rt_migrate_content_classes(context):
    """
    Migrate content created with collective.folderishtypes to plone.volto.

    REMOVE WHEN THIS PR IS MERGED: https://github.com/plone/plone.volto/pull/86

    """
    interface = "collective.folderishtypes.interfaces.IFolderishType"
    idxs = ["object_provides", "getObjPositionInParent"]
    brains = api.content.find(
        object_provides=interface, sort_on="getObjPositionInParent"
    )
    total_brains = len(brains)
    logger.info(f"Migration: {total_brains} contents to be migrated.")
    for idx, brain in enumerate(brains):
        content = brain.getObject()
        content_id = content.getId()
        content.__class__ = MIGRATION[content.portal_type]
        parent = content.aq_parent
        ordered = IOrderedContainer(parent, None)
        if ordered is not None:
            order = ordered.getObjectPosition(content.getId())
            if order == 1:
                # can be the default one and we will lose the ordering
                order = ordered.keys().index(content.getId())
        parent._delOb(content_id)
        parent._setOb(content_id, content)
        content = parent[content_id]
        ordered.moveObjectToPosition(content.getId(), order)
        content.reindexObject(idxs=idxs)

        if idx and idx % 100 == 0:
            logger.info(f"Migration: {idx + 1} / {total_brains}")

    logger.info("Migration from collective.folderishtypes to plone.volto complete")


upgrades.migrate_content_classes = rt_migrate_content_classes
