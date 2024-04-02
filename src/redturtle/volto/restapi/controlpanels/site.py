from plone.restapi.controlpanels.registry import SiteControlpanel
from redturtle.volto.interfaces import IRedturtleVoltoLayer
from redturtle.volto.interfaces import IRedTurtleVoltoSiteControlpanel
from redturtle.volto.interfaces import IRedTurtleVoltoSiteSchema
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface


@adapter(Interface, IRedturtleVoltoLayer)
@implementer(IRedTurtleVoltoSiteControlpanel)
class RedTurtleVoltoSiteControlpanel(SiteControlpanel):
    schema = IRedTurtleVoltoSiteSchema
