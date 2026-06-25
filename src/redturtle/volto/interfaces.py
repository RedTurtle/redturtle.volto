# -*- coding: utf-8 -*-
# from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from plone.app.contenttypes.interfaces import (
    IPloneAppContenttypesLayer as IDefaultBrowserLayer,
)
from plone.dexterity.interfaces import IDexterityContent
from plone.restapi.controlpanels.interfaces import IControlpanel
from plone.volto.interfaces import IPloneVoltoCoreLayer
from redturtle.volto import _
from zope.interface import Interface
from zope.schema import Bool
from zope.schema import SourceText

import json

# Default JSON configuration
DEFAULT_RANKING_CONFIG = [
    {"index": "Subject", "value": "__TERM__", "weight": 16},
    {"index": "Title", "value": "__TERM__", "weight": 8},
    {"index": "Description", "value": "__TERM__", "weight": 6},
]


class IRedturtleVoltoLayer(IDefaultBrowserLayer, IPloneVoltoCoreLayer):
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
    advanced_query_ranking_rules = SourceText(
        title=_(
            "advanced_query_ranking_rules_label", default="AdvancedQuery Ranking rules"
        ),
        description=_(
            "advanced_query_ranking_rules_help",
            default="List of AdvancedQuery ranking rules. Use '__TERM__' for current search term.",
        ),
        default=json.dumps(DEFAULT_RANKING_CONFIG, indent=2),
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


class ICustomFeedItem(IDexterityContent):
    """
    Marker interface for custom feed items.
    """
