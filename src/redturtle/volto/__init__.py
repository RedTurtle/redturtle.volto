# -*- coding: utf-8 -*-

from Acquisition import aq_base
from plone.app.content.interfaces import INameFromTitle
from plone.app.dexterity.behaviors.metadata import ICategorization
from plone.app.dexterity.textindexer import utils
from plone.app.uuid.utils import uuidToObject
from plone.restapi.bbb import base_hasattr
from plone.restapi.services.content import utils as rest_utils
from plone.uuid.interfaces import IUUID
from redturtle.volto import patches  # noqa
from zope.container.contained import notifyContainerModified
from zope.container.contained import ObjectAddedEvent
from zope.container.interfaces import INameChooser
from zope.event import notify
from zope.i18nmessageid import MessageFactory

_ = MessageFactory("redturtle.volto")

# Index also subjects in SearchableText.
utils.searchable(ICategorization, "subjects")


def add_patched(container, obj, rename=True):
    """Add an object to a container."""

    id_ = getattr(aq_base(obj), "id", None)

    # Archetypes objects are already created in a container thus we just fire
    # the notification events and rename the object if necessary.
    if base_hasattr(obj, "_at_rename_after_creation"):
        notify(ObjectAddedEvent(obj, container, id_))
        notifyContainerModified(container)
        if obj._at_rename_after_creation and rename:
            obj._renameAfterCreation(check_auto_id=True)
        return obj
    else:
        if rename:
            chooser = INameChooser(container)
            # INameFromTitle adaptable objects should not get a name
            # suggestion. NameChooser would prefer the given name instead of
            # the one provided by the INameFromTitle adapter.
            suggestion = None
            name_from_title = INameFromTitle(obj, None)
            if name_from_title is None:
                suggestion = obj.Title()
            id_ = chooser.chooseName(suggestion, obj)
            obj.id = id_

        chooser = INameChooser(container)
        id_ = chooser.chooseName(obj.id, obj)
        obj.id = id_
        new_id = container._setObject(id_, obj)
        # _setObject triggers ObjectAddedEvent which can end up triggering a
        # content rule to move the item to a different container. In this case
        # look up the object by UUID.
        try:
            return container._getOb(new_id)
        except AttributeError:
            uuid = IUUID(obj)
            return uuidToObject(uuid)


rest_utils.add = add_patched
