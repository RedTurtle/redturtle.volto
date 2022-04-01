# -*- coding: utf-8 -*-
from plone.stringinterp.adapters import BaseSubstitution
from Products.CMFCore.interfaces import IContentish
from zope.component import adapter
from plone.stringinterp import _ as stringinterp_mf
from redturtle.volto import _


@adapter(IContentish)
class VoltoUrlSubstitution(BaseSubstitution):

    category = stringinterp_mf(u"All Content")
    description = _(u"Volto URL")

    def safe_call(self):
        absolute_url = self.context.absolute_url()
        portal_url = self.context.portal_url()
        if not portal_url.endswith("/api"):
            return absolute_url
        fixed_portal_url = portal_url.replace("/api", "")
        return absolute_url.replace(portal_url, fixed_portal_url)
