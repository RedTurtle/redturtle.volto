# -*- coding: utf-8 -*-
from json.decoder import JSONDecodeError
from plone import api
from plone.base.interfaces import ISiteSchema
from plone.formwidget.namedfile.converter import b64decode_file
from plone.registry.interfaces import IRegistry
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.services.site.get import Site as BaseSite
from plone.restapi.services.site.get import SiteGet as BaseSiteGet
from redturtle.volto.interfaces import IRedTurtleVoltoAdditionalSiteSchema
from zope.component import adapter
from zope.component import getUtility
from zope.interface import implementer
from zope.interface import Interface

import json
import logging


logger = logging.getLogger(__name__)


@implementer(IExpandableElement)
@adapter(Interface, Interface)
class Site(BaseSite):
    def __call__(self, expand=False):
        """"""
        # get standard fields
        result = super().__call__(expand=expand)

        registry = getUtility(IRegistry)
        site_settings = registry.forInterface(ISiteSchema, prefix="plone", check=False)
        additional_settings = registry.forInterface(
            IRedTurtleVoltoAdditionalSiteSchema, prefix="plone", check=False
        )
        # set title and subtitle based on language, if field is set
        site_title_translated = self.get_value_from_registry(
            additional_settings, "site_title_translated"
        )
        site_subtitle = self.get_value_from_registry(
            additional_settings, "site_subtitle"
        )

        result["site"]["plone.site_title"] = (
            self.get_translated_value(site_title_translated)
            or result["site"]["plone.site_title"]  # noqa
        )
        result["site"]["plone.site_subtitle"] = self.get_translated_value(site_subtitle)

        # images
        field_mapping = {
            "logo": site_settings,
            "logo_footer": additional_settings,
            "favicon": site_settings,
        }
        site_url = api.portal.get().absolute_url()
        for field, settings_name in field_mapping.items():
            value = self.get_value_from_registry(settings_name, f"site_{field}")
            result["site"][f"plone.site_{field}"] = {}
            if value:
                filename, data = b64decode_file(value)
                result["site"][f"plone.site_{field}"][
                    "url"
                ] = f"{site_url}/@@site-{field}/{filename}"
                result["site"][f"plone.site_{field}"]["width"] = (
                    self.get_value_from_registry(
                        additional_settings, f"site_{field}_width"
                    )
                )
                result["site"][f"plone.site_{field}"]["height"] = (
                    self.get_value_from_registry(
                        additional_settings, f"site_{field}_height"
                    )
                )

        return result

    def get_value_from_registry(self, registry, field):
        try:
            return getattr(registry, field, "")
        except KeyError:
            return ""

    def get_translated_value(self, field_value):
        """
        If set, return the value for current language.
        """
        if not field_value:
            return ""
        try:
            value = json.loads(field_value)
        except (JSONDecodeError, TypeError) as e:
            logger.exception(e)
            return ""
        lang = api.portal.get_current_language()
        return value.get(lang, "")


class SiteGet(BaseSiteGet):

    def reply(self):
        site = Site(self.context, self.request)
        return site(expand=True)["site"]
