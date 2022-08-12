# -*- coding: utf-8 -*-
from redturtle.volto import _
from zope import schema
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class IRedturtleVoltoLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


class IRedTurtleVoltoSiteSchema(Interface):

    site_subtitle = schema.TextLine(
        title=_("site_subtitle_label", default="Site subtitle"),
        description=_("site_subtitle_help", default="Insert a subtitle if needed."),
        default="",
        required=False,
    )

    footer_title = schema.TextLine(
        title=_("footer_title_label", default="Footer title"),
        description=_(
            "footer_title_help",
            default="Insert title that will be shown in the footer.",
        ),
        default="",
        required=False,
    )

    footer_subtitle = schema.TextLine(
        title=_("footer_subtitle_label", default="Footer subtitle"),
        description=_(
            "footer_subtitle_help",
            default="Insert a subtitle for the footer if needed.",
        ),
        default="",
        required=False,
    )

    show_logo_on_footer = schema.Bool(
        title=_("show_logo_on_footer_label", default="Show logo on footer"),
        description=_(
            "show_logo_on_footer_help",
            default="If selected, the site logo will be used also on footer, if you don't set a footer logo.",
        ),
        default=False,
        required=False,
    )

    footer_logo = schema.Bytes(
        title=_("footer_logo_label", default="Footer Logo"),
        description=_(
            "footer_logo_help",
            default="This shows a custom logo on footer. If set, will override the previous check.",
        ),
        required=False,
    )
