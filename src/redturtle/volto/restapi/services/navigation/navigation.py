from plone.restapi.interfaces import IExpandableElement
from plone.restapi.services import Service
from plone.restapi.services.navigation.get import Navigation as BaseNavigation
from redturtle.volto.interfaces import IRedturtleVoltoLayer
from redturtle.volto.restapi.services.navigation.limits import (
    apply_navigation_items_cap,
)
from redturtle.volto.restapi.services.navigation.limits import clamp_navigation_depth
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface


@implementer(IExpandableElement)
@adapter(Interface, IRedturtleVoltoLayer)
class Navigation(BaseNavigation):
    """
    plone.restapi navigation with a limit on expand.navigation.depth and on
    the number of items (whole levels are cut).

    Packages that override the navigation should subclass this class to
    inherit the limits.
    """

    def __call__(self, expand=False):
        if expand:
            clamp_navigation_depth(self.request)
        result = super().__call__(expand=expand)
        if expand:
            apply_navigation_items_cap(
                result["navigation"]["items"], self.request, keep_empty_key=True
            )
        return result


class NavigationGet(Service):
    def reply(self):
        navigation = Navigation(self.context, self.request)
        return navigation(expand=True)["navigation"]
