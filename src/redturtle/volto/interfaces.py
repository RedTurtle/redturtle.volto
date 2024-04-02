# -*- coding: utf-8 -*-
from plone.autoform import directives as form
from plone.restapi.controlpanels import IControlpanel
from redturtle.volto import _
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.schema import Bool
from zope.schema import Bytes
from zope.schema import Int
from zope.schema import SourceText


try:
    from plone.base.interfaces.controlpanel import ISiteSchema
except ImportError:
    from Products.CMFPlone.interfaces.controlpanel import ISiteSchema


class IRedturtleVoltoLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


class IRedTurtleVoltoSettingsControlpanel(IControlpanel):
    """ """


class IRedTurtleVoltoSettings(Interface):
    enable_advanced_query_ranking = Bool(
        title=_(
            "enable_advanced_query_ranking_label",
            default="Enable AdvancedQuery ranking",
        ),
        description=_(
            "enable_advanced_query_ranking_help",
            default="If enabled, a custom ranking for SearchableText searches will be used.",
        ),
        default=False,
        required=False,
    )

    check_aliases_in_namechooser = Bool(
        title=_(
            "check_aliases_in_namechooser_label",
            default="Disallow ids used in aliases",
        ),
        description=_(
            "check_aliases_in_namechooser_help",
            default="If enabled, users can't create contents with ids that are already used as aliases.",
        ),
        default=False,
        required=False,
    )


class IRedTurtleVoltoAdditionalSiteSchema(Interface):
    """
    Settings interface that add some extra fields to site controlpanel.
    """

    site_title_translated = SourceText(
        title=_("site_localized_label", default="Translated site title"),
        description=_(
            "site_localized_help",
            default="If you want to translate site title for different available language, use this field to set translations. If set, this field overrides the default one.",
        ),
        required=False,
        default="",
    )

    site_subtitle = SourceText(
        title=_("site_subtitle_label", default="Site subtitle"),
        description=_(
            "site_subtitle_help",
            default="",
        ),
        required=False,
        default="",
    )

    site_logo_footer = Bytes(
        title=_("logo_footer_label", default="Footer logo"),
        description=_(
            "logo_footer_help",
            default="Insert a logo that will be used in the site footer.",
        ),
        required=False,
    )

    site_logo_width = Int(required=False)
    site_logo_height = Int(required=False)
    site_favicon_width = Int(required=False)
    site_favicon_height = Int(required=False)
    site_logo_footer_width = Int(required=False)
    site_logo_footer_height = Int(required=False)


class IRedTurtleVoltoSiteSchema(ISiteSchema, IRedTurtleVoltoAdditionalSiteSchema):
    """"""

    form.order_after(site_title_translated="site_title")
    form.order_after(site_subtitle="site_title_translated")
    form.order_after(site_logo_footer="site_logo")

    form.omitted("site_logo_width")
    form.omitted("site_logo_height")
    form.omitted("site_favicon_width")
    form.omitted("site_favicon_height")
    form.omitted("site_logo_footer_width")
    form.omitted("site_logo_footer_height")


class IRedTurtleVoltoSiteControlpanel(IControlpanel):
    """ """
