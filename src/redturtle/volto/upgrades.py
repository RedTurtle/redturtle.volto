# -*- coding: utf-8 -*-
from plone import api

import logging

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
        "profile-plone.app.caching:with-caching-proxy", "plone.app.registry", False
    )
