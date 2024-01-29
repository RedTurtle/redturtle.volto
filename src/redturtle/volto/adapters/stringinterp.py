# -*- coding: utf-8 -*-
from plone.stringinterp.adapters import BaseSubstitution
from Products.CMFCore.interfaces import IContentish
from redturtle.volto import _
from zope.component import adapter


try:
    from plone.stringinterp import _ as stringinterp_mf
except ImportError:
    # plone 6
    from plone.base import PloneMessageFactory as stringinterp_mf


@adapter(IContentish)
class VoltoUrlSubstitution(BaseSubstitution):
    category = stringinterp_mf("All Content")
    description = _(
        "stringinterp_volto_url",
        default='Volto URL: Content url without "/api".',
    )

    def safe_call(self):
        absolute_url = self.context.absolute_url()
        portal_url = self.context.portal_url()
        if not portal_url.endswith("/api"):
            return absolute_url
        fixed_portal_url = portal_url.replace("/api", "")
        return absolute_url.replace(portal_url, fixed_portal_url)


@adapter(IContentish)
class VoltoParentUrlSubstitution(BaseSubstitution):
    category = stringinterp_mf("All Content")
    description = _(
        "stringinterp_volto_parent_url",
        default='Volto Parent URL: Content url without "/api".',
    )

    def safe_call(self):
        absolute_url = self.context.aq_parent.absolute_url()
        portal_url = self.context.aq_parent.portal_url()
        if not portal_url.endswith("/api"):
            return absolute_url
        fixed_portal_url = portal_url.replace("/api", "")
        return absolute_url.replace(portal_url, fixed_portal_url)
