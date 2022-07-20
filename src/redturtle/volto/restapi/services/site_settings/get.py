# -*- coding: utf-8 -*-
from plone.restapi.imaging import get_scale_infos
from plone.restapi.services import Service
from redturtle.volto.adapters.scaling import LogoAnnotationStorage
from zope.annotation.interfaces import IAnnotations

import time


class SiteSettingsGet(Service):
    def reply(self):
        res = {"scales": self.get_logo_scales()}
        return res

    def get_logo_scales(self):
        annotations = IAnnotations(self.context)
        logo_last_modified = annotations.get("logo_modified_date", time.time())
        storage = LogoAnnotationStorage(
            context=self.context, modified=logo_last_modified
        )

        scales = {}
        for name, actual_width, actual_height in get_scale_infos():
            scale = storage.scale(
                fieldname="site_logo",
                height=actual_width,
                width=actual_height,
                direction="thumbnail",
                scale=name,
            )

            if scale is None:
                continue
            data = scale.get("data", None)
            extension = data.contentType.split("/")[-1].lower()
            if data.contentType == "image/svg+xml":
                extension = "svg"
            url = u"{0}/@@site-logo-scales/{1}.{2}".format(
                self.context.portal_url(), scale.get("uid", ""), extension
            )
            actual_width = scale.get("width", "")
            actual_height = scale.get("height", "")

            scales[name] = {
                "download": url,
                "width": actual_width,
                "height": actual_height,
            }
        return scales
