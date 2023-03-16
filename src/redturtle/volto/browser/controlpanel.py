# -*- coding: utf-8 -*-
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.app.registry.browser.controlpanel import RegistryEditForm
from redturtle.volto import _
from redturtle.volto.interfaces import IRedTurtleVoltoSettings


class RedturtleVoltoSettingsForm(RegistryEditForm):
    schema = IRedTurtleVoltoSettings
    id = "redturtle-volto-settings"
    label = _("RedTurtle Volto Settings")


class RedturtleVoltoSettingsView(ControlPanelFormWrapper):
    """ """

    form = RedturtleVoltoSettingsForm
