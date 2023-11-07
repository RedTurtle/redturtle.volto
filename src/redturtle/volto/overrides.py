from Acquisition import aq_base
from plone.app.contenttypes.interfaces import IFile
from plone.indexer.decorator import indexer
from plone.rfc822.interfaces import IPrimaryFieldInfo
from Products.CMFCore.utils import getToolByName
from Products.PortalTransforms.libtransforms.utils import MissingBinary
from ZODB.POSException import ConflictError

from plone.app.contenttypes.indexers import SearchableText, _unicode_save_string_concat
from redturtle.volto import logger
from hashlib import sha256
from time import time

_marker = object()


# see. Products/PortalTransforms/cache.py
class Cache:
    def __init__(self, context, value, _id="_v_transform_cache"):
        self.hash = sha256(value).hexdigest()
        self.context = context
        self._id = _id

    def setCache(self, key, value):
        """cache a value indexed by key"""
        if not value.isCacheable():
            return
        context = self.context
        if getattr(aq_base(context), self._id, None) is None:
            setattr(context, self._id, {})
        getattr(context, self._id)[key] = (time(), self.hash, value)
        return key

    def getCache(self, key):
        """try to get a cached value for key
        return _marker if not present
        else return value
        """
        obj = self.context
        dict = getattr(obj, self._id, None)
        if dict is None:
            return _marker
        try:
            _, hash, value = dict.get(key, None)
            if hash != self.hash:
                return _marker
            return value
        except TypeError:
            return _marker


# plone.app.contenttypes-3.0.5-py3.11.egg/plone/app/contenttypes/indexers.py
@indexer(IFile)
def SearchableText_file(obj):
    try:
        primary_field = IPrimaryFieldInfo(obj)
    except TypeError:
        logger.warn(
            "Lookup of PrimaryField failed for {} "
            "If renaming or importing please reindex!".format(obj.absolute_url())
        )
        return
    if primary_field.value is None:
        return SearchableText(obj)
    mimetype = primary_field.value.contentType
    transforms = getToolByName(obj, "portal_transforms")
    if transforms._findPath(mimetype, "text/plain") is None:
        # check if there is a valid transform available first
        return SearchableText(obj)
    value = primary_field.value.data
    filename = primary_field.value.filename
    try:
        # CHANGES FROM HERE ...
        cache = Cache(obj, value)
        transformed_value = cache.getCache(key=(primary_field.fieldname, mimetype))
        if transformed_value is _marker:
            logger.info("MISSING CACHE: %s", obj.absolute_url())
            transformed_value = transforms.convertTo(
                "text/plain", value, mimetype=mimetype, filename=filename
            )
            cache.setCache((primary_field.fieldname, mimetype), transformed_value)
        else:
            logger.info("HIT CACHE: %s", obj.absolute_url())
        # ... TO HERE.
        if not transformed_value:
            return SearchableText(obj)
        return _unicode_save_string_concat(
            SearchableText(obj), transformed_value.getData()
        )
    except MissingBinary:
        return SearchableText(obj)
    except (ConflictError, KeyboardInterrupt):
        raise
    except Exception as msg:
        logger.exception(
            'exception while trying to convert blob contents to "text/plain" '
            "for {}. Error: {}".format(obj, str(msg)),
        )
        return SearchableText(obj)