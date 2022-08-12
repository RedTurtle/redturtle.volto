from redturtle.volto import _
from redturtle.volto.interfaces import IRedTurtleVoltoSiteSchema
from plone.app.registry.browser import controlpanel
from plone.formwidget.namedfile.widget import NamedImageFieldWidget


class RedTurtleVoltoSiteControlPanelForm(controlpanel.RegistryEditForm):

    id = "RedTurtleVoltoSiteControlPanel"
    label = _(
        "site_settings_controlpanel_label", default="Site Settings (RedTurtle Volto)"
    )
    description = _(
        "site_settings_controlpanel_help", default="Additional Site-wide settings."
    )
    schema = IRedTurtleVoltoSiteSchema
    schema_prefix = "redturtle-volto"

    def updateFields(self):
        super().updateFields()
        self.fields["footer_logo"].widgetFactory = NamedImageFieldWidget


class RedTurtleVoltoSiteControlPanel(controlpanel.ControlPanelFormWrapper):
    form = RedTurtleVoltoSiteControlPanelForm
