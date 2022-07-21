# -*- coding: utf-8 -*-
from plone.formwidget.namedfile.converter import b64decode_file
from plone.namedfile.file import NamedBlobImage
from plone.namedfile.scaling import DefaultImageScalingFactory
from plone.registry.interfaces import IRegistry
from plone.scale.interfaces import IImageScaleFactory
from plone.scale.storage import AnnotationStorage
from plone.scale.storage import IImageScaleStorage
from Products.CMFPlone.interfaces import ISiteSchema
from zope.component import getUtility
from zope.interface import implementer

import logging


logger = logging.getLogger(__name__)
_marker = object()


@implementer(IImageScaleStorage)
class LogoAnnotationStorage(AnnotationStorage):
    @property
    def modified_time(self):
        return self.modified


@implementer(IImageScaleFactory)
class LogoImageScalingFactory(DefaultImageScalingFactory):
    def __call__(
        self,
        fieldname,
        filename,
        img_data,
        direction="thumbnail",
        height=None,
        width=None,
        scale=None,
        **parameters
    ):

        if "quality" not in parameters:
            quality = self.get_quality()
            if quality:
                parameters["quality"] = quality
        if filename.endswith(".svg") and img_data.startswith(b"<svg"):
            result = img_data, "svg+xml", (width, height)
        else:
            result = self.create_scale(
                img_data, direction=direction, height=height, width=width, **parameters
            )

        data, format_, dimensions = result
        mimetype = "image/{0}".format(format_.lower())
        value = NamedBlobImage(data, contentType=mimetype, filename=filename)
        value.fieldname = fieldname
        return value, format_, dimensions
