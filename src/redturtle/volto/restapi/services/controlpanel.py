# -*- coding: utf-8 -*-
from plone.restapi.controlpanels import RegistryConfigletPanel
from redturtle.volto.interfaces import IRedTurtleVoltoSettings
from redturtle.volto.interfaces import IRedTurtleVoltoSettingsControlpanel
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface


@adapter(Interface, Interface)
@implementer(IRedTurtleVoltoSettingsControlpanel)
class RedTurtleVoltoSettings(RegistryConfigletPanel):
    schema = IRedTurtleVoltoSettings
    configlet_id = "RedTurtleVoltoSettings"
    configlet_category_id = "Products"
    schema_prefix = None
