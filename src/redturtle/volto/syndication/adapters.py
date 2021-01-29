# -*- coding: utf-8 -*-
from Products.CMFPlone.browser.syndication.adapters import DexterityItem as BaseDexterityItem
from Products.CMFPlone.interfaces.syndication import IFeed
from plone import api
from plone.dexterity.interfaces import IDexterityContent
from zope.component import adapts


class IDexterityContentSyndacable(IDexterityContent):
    """
    Marker interface to have a more specific hook
    for the adapter below
    """

class DexterityItem(BaseDexterityItem):
    """
    We need to customize this adapter to use in some specific case
    plone collections and /RSS view.
    To call a /RSS we need to call the customer site with '/api'
    sub path. This means that result links contains '/api' and we
    need to remove it
    """
    adapts(IDexterityContentSyndacable, IFeed)

    def __init__(self, context, feed):
        super(DexterityItem, self).__init__(context, feed)
        self.portal_url = api.portal.get().absolute_url()

    @property
    def link(self):
        link = super(DexterityItem, self).link
        return link.replace(
            "{portal_url}/api/".format(portal_url=self.portal_url), 
            "{portal_url}/".format(portal_url=self.portal_url)
        )
        
    guid = link
