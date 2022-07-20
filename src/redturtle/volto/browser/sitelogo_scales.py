# -*- coding: utf-8 -*-
from Products.CMFPlone.interfaces import ISiteSchema
from plone.formwidget.namedfile.converter import b64decode_file
from plone.namedfile.browser import Download
from plone.namedfile.file import NamedImage
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from plone.namedfile.scaling import ImageScale
from plone.namedfile.scaling import ImageScaling


class ImageScaleLogo(ImageScale):
    def validate_access(self):
        return True


class SiteLogoScaling(ImageScaling):
    _scale_view_class = ImageScaleLogo
