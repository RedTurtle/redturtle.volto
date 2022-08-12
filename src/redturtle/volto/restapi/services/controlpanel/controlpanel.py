# -*- coding: utf-8 -*-
from redturtle.volto.interfaces import (
    IRedturtleVoltoLayer,
    IRedTurtleVoltoSiteSchema,
)
from plone.restapi.controlpanels import RegistryConfigletPanel
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface


@adapter(Interface, IRedturtleVoltoLayer)
@implementer(IRedTurtleVoltoSiteSchema)
class RedTurtleVoltoSiteControlPanel(RegistryConfigletPanel):
    schema = IRedTurtleVoltoSiteSchema
    configlet_id = "PloneReconfigRedTurtleVolto"
    configlet_category_id = "plone-general"
    schema_prefix = "redturtle-volto"
