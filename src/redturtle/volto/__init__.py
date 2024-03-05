# -*- coding: utf-8 -*-
"""Init and utils."""
from plone.app.content.browser.vocabulary import PERMISSIONS
from plone.folder.nogopip import GopipIndex
from Products.ZCatalog.Catalog import Catalog
from redturtle.volto.catalogplan import Catalog_sorted_search_indexes
from zope.i18nmessageid import MessageFactory
from ZTUtils.Lazy import LazyCat
from ZTUtils.Lazy import LazyMap

import logging


logger = logging.getLogger(__name__)


_ = MessageFactory("redturtle.volto")

PERMISSIONS["plone.app.vocabularies.Keywords"] = "View"

# CATALOG PATCHES

logger.info(
    "install monkey patch for Products.ZCatalog.Catalog.Catalog._sorted_search_indexes #### WORK IN PROGRESS ####"
)
Catalog._orig_sorted_search_indexes = Catalog._sorted_search_indexes
Catalog._sorted_search_indexes = Catalog_sorted_search_indexes

MAX_SORTABLE = 5000


def Catalog_sortResults(
    self,
    rs,
    sort_index,
    reverse=False,
    limit=None,
    merge=True,
    actual_result_count=None,
    b_start=0,
    b_size=None,
):
    if MAX_SORTABLE > 0:
        if actual_result_count is None:
            actual_result_count = len(rs)
        if actual_result_count >= MAX_SORTABLE and isinstance(sort_index, GopipIndex):
            logger.warning(
                "too many results %s disable GopipIndex sorting", actual_result_count
            )
            switched_reverse = bool(
                b_size and b_start and b_start > actual_result_count / 2
            )
            if hasattr(rs, "keys"):
                sequence, slen = self._limit_sequence(
                    rs.keys(), actual_result_count, b_start, b_size, switched_reverse
                )
                return LazyMap(
                    self.__getitem__,
                    sequence,
                    len(sequence),
                    actual_result_count=actual_result_count,
                )
            else:
                logger.error(
                    "too many results %s disable GopipIndex sorting results %s has no key",
                    actual_result_count,
                    type(rs),
                )
                return LazyCat([], 0, actual_result_count)
    return self._orig_sortResults(
        rs, sort_index, reverse, limit, merge, actual_result_count, b_start, b_size
    )


logger.info("install monkey patch for Products.ZCatalog.Catalog.Catalog.sortResults")
Catalog._orig_sortResults = Catalog.sortResults
Catalog.sortResults = Catalog_sortResults
