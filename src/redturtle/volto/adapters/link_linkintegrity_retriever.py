"""Link Integrity - link retriever methods."""

from plone.app.contenttypes.interfaces import ILink
from plone.app.linkintegrity.interfaces import IRetriever
from zope.component import adapter
from zope.interface import implementer


@implementer(IRetriever)
@adapter(ILink)
class LinkRetriever:
    """"""

    def __init__(self, context):
        self.context = context

    def retrieveLinks(self):
        """
        If Link object refers to an internal object, enable linkintegrity
        """
        remote_url = self.context.remoteUrl
        if remote_url and "resolveuid" in remote_url:
            return [remote_url]
        return []
