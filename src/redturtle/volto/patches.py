# These are patches not managed by collective.monkeypatcher
from experimental.noacquisition import config
from plone.app.content.browser.vocabulary import PERMISSIONS
from plone.app.redirector.interfaces import IRedirectionStorage
from plone.folder.nogopip import GopipIndex
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.controlpanel.browser import redirects
from Products.ZCatalog.Catalog import Catalog
from redturtle.volto.catalogplan import Catalog_sorted_search_indexes
from urllib.parse import urlparse
from zope.component import getUtility
from zope.component.hooks import getSite
from zope.i18nmessageid import MessageFactory
from ZTUtils.Lazy import LazyCat
from ZTUtils.Lazy import LazyMap

import logging


logger = logging.getLogger(__name__)

_ = MessageFactory("plone")


def absolutize_path_patched(path, is_source=True):
    """Create path including the path of the portal root.

    The path must be absolute, so starting with a slash.
    Or it can be a full url.

    If is_source is true, this is an alternative url
    that will point to a target (unknown here).

    If is_source is true, path is the path of a target.
    An object must exist at this path, unless it is a full url.

    Return a 2-tuple: (absolute redirection path,
    an error message if something goes wrong and otherwise '').
    """

    portal = getSite()
    err = None
    is_external_url = False
    if not path:
        if is_source:
            err = _("You have to enter an alternative url.")
        else:
            err = _("You have to enter a target.")
    elif not path.startswith("/"):
        if is_source:
            err = _("Alternative url path must start with a slash.")
        else:
            # For targets, we accept external urls.
            # Do basic check.
            parsed = urlparse(path)
            if parsed.scheme in ("https", "http") and parsed.netloc:
                is_external_url = True
            else:
                err = _("Target path must start with a slash.")
    elif "@@" in path:
        if is_source:
            err = _("Alternative url path must not be a view.")
        else:
            err = _("Target path must not be a view.")
    else:
        context_path = "/".join(portal.getPhysicalPath())
        path = f"{context_path}{path}"
    if not err and not is_external_url:
        catalog = getToolByName(portal, "portal_catalog")
        if is_source:
            # Check whether already exists in storage
            storage = getUtility(IRedirectionStorage)
            if storage.get(path):
                err = _("The provided alternative url already exists!")
            else:
                # Check whether obj exists at source path.
                # A redirect would be useless then.

                # THIS IS THE PATCH
                # unrestrictedTraverse returns the object with acquisition, so if
                # you have a content with path /Plone/aaa and try to call unrestrictedTraverse
                # with /Plone/aaa/aaa/aaa/aaa it will always return /Plone/aaa object
                # and this is not correct because we could want to create an alias for /Plone/aaa
                # that is /Plone/aaa/aaa
                # In Plone7 this will not be a problem anymore because of this:
                # https://github.com/plone/Products.CMFPlone/issues/3871
                item = portal.unrestrictedTraverse(path, None)
                # if item is not None: this is the original check
                if item is not None and "/".join(item.getPhysicalPath()) == path:
                    # if paths are different, it's an acquisition false positive,
                    # so go on and let create the alias
                    err = _("Cannot use a working path as alternative url.")
                # END OF PATCH
        else:
            # Check whether obj exists at target path
            result = catalog.searchResults(path={"query": path})
            if len(result) == 0:
                err = _("The provided target object does not exist.")

    return path, err


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


# apply patches
logger.info(
    "install monkey patch for Products.ZCatalog.Catalog.Catalog._sorted_search_indexes #### WORK IN PROGRESS ####"
)
Catalog._orig_sorted_search_indexes = Catalog._sorted_search_indexes
Catalog._sorted_search_indexes = Catalog_sorted_search_indexes

logger.info("install monkey patch for Products.ZCatalog.Catalog.Catalog.sortResults")
Catalog._orig_sortResults = Catalog.sortResults
Catalog.sortResults = Catalog_sortResults

logger.info("install monkey patch for plone.app.content.browser.vocabulary.PERMISSIONS")
PERMISSIONS["plone.app.vocabularies.Keywords"] = "View"

logger.info(
    "install monkey patch for from Products.CMFPlone.controlpanel.browser.redirects.absolutize_path"
)
redirects.absolutize_path = absolutize_path_patched

logger.info("enable experimental.noacquisition")
config.DRYRUN = False
