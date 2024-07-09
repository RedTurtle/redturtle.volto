from Acquisition import aq_inner
from plone import api
from plone.app.content.namechooser import (
    NormalizingNameChooser as BaseNormalizingNameChooser,
)
from plone.app.redirector.interfaces import IRedirectionStorage
from redturtle.volto import _
from redturtle.volto.interfaces import IRedTurtleVoltoSettings
from zExceptions import BadRequest
from zope.component import getUtility


def check_alias(context, id):
    context = aq_inner(context)
    try:
        if not api.portal.get_registry_record(
            "check_aliases_in_namechooser",
            interface=IRedTurtleVoltoSettings,
            default=False,
        ):
            return
    except KeyError:
        return
    storage = getUtility(IRedirectionStorage)
    path = "/".join(context.getPhysicalPath()) + "/" + id
    if storage.get(path):
        portal_path = "/".join(api.portal.get().getPhysicalPath())
        fixed_path = path.replace(portal_path, "")
        msg = _(
            "name_chooser_alias_error",
            default='The id "${id}" is invalid because there is already an alias for that path. '
            'Change its id or ask site administrators to remove "${fixed_path}" in aliases management.',
            mapping={"id": id, "fixed_path": fixed_path},
        )
        raise BadRequest(api.portal.translate(msg))


class NormalizingNameChooser(BaseNormalizingNameChooser):
    def chooseName(self, name, obj):
        """
        Additional check: the id should not be in redirection tool.
        """
        id = super().chooseName(name=name, obj=obj)

        # this raise BadRequest if there is an override with aliases
        check_alias(context=self.context, id=id)
        return id
