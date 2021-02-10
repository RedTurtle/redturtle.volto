# -*- coding: utf-8 -*-
from redturtle.volto.setuphandlers import set_robots
import logging

logger = logging.getLogger(__name__)

DEFAULT_PROFILE = "profile-design.plone.contenttypes:default"


def update_profile(context, profile):
    context.runImportStepFromProfile(DEFAULT_PROFILE, profile)


def update_types(context):
    update_profile(context, "typeinfo")


def update_rolemap(context):
    update_profile(context, "rolemap")


def update_registry(context):
    update_profile(context, "plone.app.registry")


def update_controlpanel(context):
    update_profile(context, "controlpanel")


def to_1003(context):
    set_robots()
