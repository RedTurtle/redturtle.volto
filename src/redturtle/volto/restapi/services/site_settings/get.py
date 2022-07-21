from plone import api
from plone.formwidget.namedfile.converter import b64decode_file
from plone.registry.interfaces import IRegistry
from plone.restapi.imaging import get_scale_infos
from plone.restapi.services import Service
from Products.CMFPlone.interfaces import ISiteSchema
from zope.component import getUtility

import time


class SiteSettingsGet(Service):
    def reply(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ISiteSchema, prefix="plone")

        res = {
            "site_logo": self.get_logo_scales(settings=settings),
            "site_title": getattr(settings, "site_title", ""),
        }
        return res

    def get_logo_scales(self, settings, fieldname="site_logo"):
        res = {}
        logo = getattr(settings, fieldname, "")
        if not logo:
            return {}

        filename, img_data = b64decode_file(logo)
        res["filename"] = filename
        res["download"] = "{0}/@@site-logo/{1}".format(
            self.context.portal_url(), filename
        )
        scales = {}
        view = api.content.get_view(
            name="images", context=self.context, request=self.request
        )
        for name, actual_width, actual_height in get_scale_infos():
            scale = view.scale(
                fieldname=fieldname,
                height=actual_width,
                width=actual_height,
                direction="thumbnail",
                scale=name,
            )

            if scale is None:
                continue
            extension = scale.data.contentType.split("/")[-1].lower()
            if scale.data.contentType == "image/svg+xml":
                extension = "svg"
            url = "{0}/@@images/{1}.{2}".format(
                self.context.portal_url(), scale.uid, extension
            )
            actual_width = scale.width
            actual_height = scale.height

            scales[name] = {
                "download": url,
                "width": actual_width,
                "height": actual_height,
            }
        if scales:
            res["scales"] = scales
        return res
