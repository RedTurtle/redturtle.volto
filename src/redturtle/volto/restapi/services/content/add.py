from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.restapi.deserializer import json_body
from plone.restapi.services.content.add import FolderPost as BaseFolderPost
from redturtle.volto.adapters.namechooser import check_alias
from zope.component import getUtility

import json


def fix_id(request, container):
    data = json_body(request)
    id_ = data.get("id")
    if not id_:
        return

    normalizer = getUtility(IIDNormalizer)
    id_pulito = normalizer.normalize(id_)

    # Same check of INameChooser.
    check_alias(context=container, id=id_pulito)

    if id_pulito != id_:
        data["id"] = id_pulito
        request.set("BODY", json.dumps(data).encode("utf-8"))


class FolderPost(BaseFolderPost):
    def reply(self):
        fix_id(self.request, container=self.context)
        return super().reply()
