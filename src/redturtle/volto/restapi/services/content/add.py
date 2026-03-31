from plone.restapi.deserializer import json_body
from plone.restapi.services.content.add import FolderPost as BaseFolderPost
from zExceptions import BadRequest


class FolderPost(BaseFolderPost):
    """Creates a new content object."""

    def reply(self):
        data = json_body(self.request)

        short_name = data.get("id", None)
        if short_name and " " in short_name:
            self.request.response.setStatus(400)

            msg = "Il nome breve non deve contenere spazi"
            raise BadRequest(msg)

        return super().reply()
