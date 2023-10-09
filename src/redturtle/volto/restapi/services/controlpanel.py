# -*- coding: utf-8 -*-
from plone.restapi.controlpanels import RegistryConfigletPanel
from zope.component import adapter
from zope.interface import Interface, implementer

from redturtle.volto.interfaces import (
    IRedTurtleVoltoSettings,
    IRedTurtleVoltoSettingsControlpanel,
)


@adapter(Interface, Interface)
@implementer(IRedTurtleVoltoSettingsControlpanel)
class RedTurtleVoltoSettings(RegistryConfigletPanel):
    schema = IRedTurtleVoltoSettings
    configlet_id = "RedTurtleVoltoSettings"
    configlet_category_id = "Products"
    schema_prefix = None
