from plone.restapi.services.copymove.copymove import Copy as BaseCopy
from plone.restapi.services.copymove.copymove import Move as BaseMove
from redturtle.volto.adapters.namechooser import check_alias


class Copy(BaseCopy):
    """Copies existing content objects."""

    def clipboard(self, parent, ids):
        for id in ids:
            check_alias(context=self.context, id=id)
        return super().clipboard(parent, ids)


class Move(BaseMove):
    """Moves existing content objects."""

    def clipboard(self, parent, ids):
        for id in ids:
            check_alias(context=self.context, id=id)
        return super().clipboard(parent, ids)
