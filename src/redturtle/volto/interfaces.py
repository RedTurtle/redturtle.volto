# -*- coding: utf-8 -*-
from plone.restapi.controlpanels.interfaces import IControlpanel
from redturtle.volto import _
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.schema import Bool


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
