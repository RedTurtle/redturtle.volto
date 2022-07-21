from plone import api
from plone.formwidget.namedfile.converter import b64decode_file
from plone.namedfile.scaling import ImageScale
from plone.namedfile.scaling import ImageScaling
from plone.protect.interfaces import IDisableCSRFProtection
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.interfaces import ISiteSchema
from redturtle.volto.adapters.scaling import LogoAnnotationStorage
from zope.annotation.interfaces import IAnnotations
from zope.component import getUtility
from zope.interface import alsoProvides

import logging
import time

logger = logging.getLogger(__name__)


class ImageScaleLogo(ImageScale):
    def validate_access(self):
        if self.fieldname == "site_logo":

            return True
        return super().validate_access()


class SiteLogoScaling(ImageScaling):
    _scale_view_class = ImageScaleLogo

    def scale(
        self,
        fieldname=None,
        scale=None,
        height=None,
        width=None,
        direction="thumbnail",
        **parameters
    ):
        if fieldname == "site_logo":
            return self.logo_scale(
                fieldname=fieldname,
                scale=scale,
                height=height,
                width=width,
                direction=direction,
                **parameters
            )
        return super().scale(
            fieldname=fieldname,
            scale=scale,
            height=height,
            width=width,
            direction=direction,
            **parameters
        )

    def logo_scale(
        self,
        fieldname=None,
        scale=None,
        height=None,
        width=None,
        direction="thumbnail",
        **parameters
    ):
        if fieldname is None:
            return  # 404
        if scale is not None:
            if width is not None or height is not None:
                logger.warn(
                    "A scale name and width/heigth are given. Those are"
                    "mutually exclusive: solved by ignoring width/heigth and "
                    "taking name",
                )
            available = self.available_sizes
            if scale not in available:
                return None  # 404
            width, height = available[scale]
        if IDisableCSRFProtection and self.request is not None:
            alsoProvides(self.request, IDisableCSRFProtection)

        annotations = IAnnotations(self.context)
        logo_last_modified = annotations.get("logo_modified_date", time.time())
        storage = LogoAnnotationStorage(
            context=self.context, modified=logo_last_modified
        )
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ISiteSchema, prefix="plone")

        logo = getattr(settings, fieldname, "")
        if not logo:
            return

        filename, img_data = b64decode_file(logo)
        info = storage.scale(
            filename=filename,
            img_data=img_data,
            fieldname=fieldname,
            height=height,
            width=width,
            direction=direction,
            scale=scale,
            **parameters
        )

        if info is None:
            return  # 404

        info["srcset"] = self.calculate_srcset(
            fieldname=fieldname,
            height=height,
            width=width,
            direction=direction,
            scale=scale,
            storage=storage,
            **parameters
        )
        info["fieldname"] = fieldname
        scale_view = self._scale_view_class(self.context, self.request, **info)
        return scale_view
