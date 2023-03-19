# -*- coding: utf-8 -*-
"""Init and utils."""
from plone.app.content.browser.vocabulary import PERMISSIONS
from zope.i18nmessageid import MessageFactory

import logging


logger = logging.getLogger(__name__)


_ = MessageFactory("redturtle.volto")

PERMISSIONS["plone.app.vocabularies.Keywords"] = "View"
