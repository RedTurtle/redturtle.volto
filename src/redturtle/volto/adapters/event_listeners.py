from zope.component import adapter
from plone.registry.interfaces import IRecordModifiedEvent
from Products.CMFPlone.interfaces.controlpanel import ISiteSchema
from zope.annotation.interfaces import IAnnotations
from plone import api

import time


@adapter(ISiteSchema, IRecordModifiedEvent)
def detectSiteLogoChange(event):
    try:
        if event.record.interface != ISiteSchema:
            return
    except AttributeError:
        return
    if event.record.fieldName != "site_logo":
        return
    portal = api.portal.get()
    annotations = IAnnotations(portal)
    annotations["logo_modified_date"] = time.time()
