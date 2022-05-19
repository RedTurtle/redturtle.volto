# -*- coding: utf-8 -*-
from plone.stringinterp.adapters import BaseSubstitution
from Products.CMFCore.interfaces import IContentish
from zope.component import adapter
from plone.stringinterp import _ as stringinterp_mf
from redturtle.volto import _


@adapter(IContentish)
class VoltoUrlSubstitution(BaseSubstitution):

    category = stringinterp_mf(u"All Content")
    description = _(
        "stringinterp_volto_url",
        default=u'Volto URL: Content url without "/api".',
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

    category = stringinterp_mf(u"All Content")
    description = _(
        "stringinterp_volto_parent_url",
        default=u'Volto Parent URL: Content url without "/api".',
    )

    def safe_call(self):
        absolute_url = self.context.aq_parent.absolute_url()
        portal_url = self.context.aq_parent.portal_url()
        if not portal_url.endswith("/api"):
            return absolute_url
        fixed_portal_url = portal_url.replace("/api", "")
        return absolute_url.replace(portal_url, fixed_portal_url)
