# -*- coding: utf-8 -*-
import logging

logger = logging.getLogger(__name__)

DEFAULT_PROFILE = "profile-design.plone.contenttypes:default"


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
