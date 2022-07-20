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
        direction="thumbnail",
        height=None,
        width=None,
        scale=None,
        **parameters
    ):

        registry = getUtility(IRegistry)
        settings = registry.forInterface(ISiteSchema, prefix="plone")
        logo = getattr(settings, "site_logo", "")
        if not logo:
            return
        filename, data = b64decode_file(logo)

        """Factory for image scales`."""
        # If quality wasn't in the parameters, try the site's default scaling
        # quality if it exists.
        if "quality" not in parameters:
            quality = self.get_quality()
            if quality:
                parameters["quality"] = quality

        result = self.create_scale(
            data, direction=direction, height=height, width=width, **parameters
        )

        # if not getattr(orig_value, "contentType", "") == "image/svg+xml":
        #     try:
        #         result = self.create_scale(
        #             orig_data,
        #             direction=direction,
        #             height=height,
        #             width=width,
        #             **parameters
        #         )
        #     except (ConflictError, KeyboardInterrupt):
        #         raise
        #     except Exception:
        #         logger.exception(
        #             'Could not scale "{0!r}" of {1!r}'.format(
        #                 orig_value, self.context.absolute_url()
        #             )
        #         )
        #         return
        #     if result is None:
        #         return
        # else:
        #     result = orig_data.read(), "svg+xml", (width, height)

        data, format_, dimensions = result
        mimetype = "image/{0}".format(format_.lower())
        value = NamedBlobImage(data, contentType=mimetype, filename=filename)
        value.fieldname = fieldname
        return value, format_, dimensions
