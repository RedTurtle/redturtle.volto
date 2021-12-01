# -*- coding: utf-8 -*-
"""Init and utils."""
from zope.i18nmessageid import MessageFactory
from plone.app.content.browser.vocabulary import PERMISSIONS


_ = MessageFactory("redturtle.volto")

PERMISSIONS["plone.app.vocabularies.Keywords"] = "View"
