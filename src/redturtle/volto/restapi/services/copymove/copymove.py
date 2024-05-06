from plone.restapi.services.copymove.copymove import Copy as BaseCopy
from plone.restapi.services.copymove.copymove import Move as BaseMove
from redturtle.volto.adapters.namechooser import check_alias


class Copy(BaseCopy):
    """Copies existing content objects."""

    def clipboard(self, parent, ids):
        for id in ids:
            check_alias(context=parent, id=id)
        return parent.manage_copyObjects(ids=ids)


class Move(BaseMove):
    """Moves existing content objects."""

    def clipboard(self, parent, ids):
        for id in ids:
            check_alias(context=parent, id=id)
        return parent.manage_cutObjects(ids=ids)
