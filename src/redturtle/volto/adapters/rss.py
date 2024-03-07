from plone.base.interfaces.syndication import IFeed
from plone.app.contenttypes.interfaces import IEvent
from Products.CMFPlone.browser.syndication.adapters import DexterityItem
from zope.component import adapter
from DateTime import DateTime


@adapter(IEvent, IFeed)
class EventItem(DexterityItem):

    @property
    def startdate(self):
        """
        Same format as other dates in 
        Products.CMFPlone.browser.syndication.adapters
        """
        date = self.context.start.isoformat()
        if date:
            return DateTime(date)
