# -*- coding: utf-8 -*-
from plone.namedfile.scaling import ImageScale
from plone.namedfile.scaling import ImageScaling


class ImageScaleLogo(ImageScale):
    def validate_access(self):
        return True


class SiteLogoScaling(ImageScaling):
    _scale_view_class = ImageScaleLogo
