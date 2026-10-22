from plone.restapi.interfaces import IExpandableElement
from plone.restapi.services import Service
from plone.restapi.services.navroot.get import Navroot as BaseNavroot
from redturtle.volto.interfaces import IRedturtleVoltoLayer
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface


# The frontend only needs @id and title of the navigation root: blocks are
# useless there and, on homepages, they duplicate the whole page payload.
EXCLUDED_FIELDS = ("blocks", "blocks_layout")


@implementer(IExpandableElement)
@adapter(Interface, IRedturtleVoltoLayer)
class Navroot(BaseNavroot):
    def __call__(self, expand=False):
        result = super().__call__(expand=expand)
        if not expand:
            return result
        navroot = result["navroot"].get("navroot", None)
        if navroot:
            for field in EXCLUDED_FIELDS:
                navroot.pop(field, None)
        return result


class NavrootGet(Service):
    def reply(self):
        navroot = Navroot(self.context, self.request)
        return navroot(expand=True)["navroot"]
