# -*- coding: utf-8 -*-
from redturtle.volto.interfaces import (
    IRedTurtleVoltoSettings,
    IRedTurtleVoltoSettingsControlpanel,
)
from plone.restapi.controlpanels import RegistryConfigletPanel
from zope.component import adapter
from zope.interface import Interface
from zope.interface import implementer


@adapter(Interface, Interface)
@implementer(IRedTurtleVoltoSettingsControlpanel)
class RedTurtleVoltoSettings(RegistryConfigletPanel):
    schema = IRedTurtleVoltoSettings
    configlet_id = "RedTurtleVoltoSettings"
    configlet_category_id = "Products"
    schema_prefix = None
