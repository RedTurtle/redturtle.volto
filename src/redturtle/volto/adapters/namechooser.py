from plone.app.content.namechooser import (
    NormalizingNameChooser as BaseNormalizingNameChooser,
)
from plone import api
from plone.app.redirector.interfaces import IRedirectionStorage
from zope.component import getUtility
from zExceptions import BadRequest
from Acquisition import aq_inner
from redturtle.volto import _
from redturtle.volto.interfaces import IRedTurtleVoltoSettings


class NormalizingNameChooser(BaseNormalizingNameChooser):

    def chooseName(self, name, obj):
        """
        Additional check: the id should not be in redirection tool.
        """
        id = super().chooseName(name=name, obj=obj)
        try:
            if not api.portal.get_registry_record(
                "check_aliases_in_namechooser",
                interface=IRedTurtleVoltoSettings,
                default=False,
            ):
                return id
        except KeyError:
            return id
        parent = aq_inner(self.context)
        storage = getUtility(IRedirectionStorage)
        path = "/".join(parent.getPhysicalPath()) + "/" + id
        if storage.get(path):
            portal_path = "/".join(api.portal.get().getPhysicalPath())
            fixed_path = path.replace(portal_path, "")
            msg = _(
                "name_chooser_alias_error",
                default='The id "${id}" is invalid because there is already an alias for that path. '
                'Search "${fixed_path}" in aliases management to manage it.',
                mapping={"id": id, "fixed_path": fixed_path},
            )
            raise BadRequest(api.portal.translate(msg))
        return id
