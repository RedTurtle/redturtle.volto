# -*- coding: utf-8 -*-
from Acquisition import aq_base
from lxml import etree
from lxml import html
from lxml.html.clean import Cleaner
from plone.app.event.base import dt_start_of_day
from plone.app.event.recurrence import Occurrence
from plone.app.caching import purge
from plone.event.interfaces import IEventAccessor
from plone.event.recurrence import recurrence_sequence_ical
from plone.event.utils import pydt
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.interfaces import IConstrainTypes
from Products.CMFPlone.interfaces import IFilterSchema
from Products.CMFPlone.utils import safe_encode
from Products.PortalTransforms.libtransforms.utils import bodyfinder
from Products.PortalTransforms.transforms.safe_html import hasScript
from zope.component import getUtility
from zope.globalrequest import getRequest

import datetime
import six


def scrub_html(self, orig):
    # append html tag to create a dummy parent for the tree
    html_parser = html.HTMLParser(encoding="utf-8")
    orig = safe_encode(orig)
    tag = b"<html"
    if tag in orig.lower():
        # full html
        tree = html.fromstring(orig, parser=html_parser)
        strip_outer = bodyfinder
    else:
        # partial html (i.e. coming from WYSIWYG editor)
        tree = html.fragment_fromstring(
            orig, create_parent=True, parser=html_parser
        )

        def strip_outer(s):
            return s[5:-6]

    for elem in tree.iter(etree.Element):
        if elem is not None:
            for attrib, value in elem.attrib.items():
                if hasScript(value):
                    del elem.attrib[attrib]

    registry = getUtility(IRegistry)
    self.settings = registry.forInterface(IFilterSchema, prefix="plone")

    valid_tags = self.settings.valid_tags
    nasty_tags = [t for t in self.settings.nasty_tags if t not in valid_tags]
    if six.PY2:
        safe_attrs = [attr.decode() for attr in html.defs.safe_attrs]
    else:
        safe_attrs = [i for i in html.defs.safe_attrs]
    safe_attrs.extend(self.settings.custom_attributes)
    remove_script = "script" in nasty_tags and 1 or 0
    cleaner = Cleaner(
        kill_tags=nasty_tags,
        remove_tags=[],
        allow_tags=valid_tags,
        page_structure=False,
        safe_attrs_only=True,
        safe_attrs=safe_attrs,
        embedded=False,
        remove_unknown_tags=False,
        meta=False,
        javascript=remove_script,
        scripts=remove_script,
        forms=False,
        style=False,
    )
    try:
        cleaner(tree)
    except AssertionError:
        # some VERY invalid HTML
        return ""
    # remove all except body or outer div
    # changes in
    # https://github.com/plone/Products.PortalTransforms/pull/43
    if six.PY2:
        result = etree.tostring(tree, encoding="utf-8", method="html").strip()
    else:
        result = etree.tounicode(tree, method="html").strip()
    return strip_outer(result)


def occurrences(self, range_start=None, range_end=None):
    """Return all occurrences of an event, possibly within a start and end
    limit.

    :param range_start: Optional start datetime, from which you want
                        occurrences be returned.
    :type range_start: Python datetime
    :param range_end: Optional start datetime, from which you want
                        occurrences be returned.
    :type range_end: Python datetime
    :returns: List of occurrences, including the start event.
    :rtype: IEvent or IOccurrence based objects

    Please note: Events beginning before range_start but ending afterwards
                    won't be found.

    TODO: really?

    TODO: test with event start = 21st feb, event end = start+36h,
    recurring for 10 days, range_start = 1st mar, range_end = last Mark
    """
    event = IEventAccessor(self.context)

    # We try to get IEventBasic start without including recurrence
    event_start = getattr(self.context, "start", None)
    if not event_start:
        event_start = event.start
    elif getattr(event, "whole_day", None):
        event_start = dt_start_of_day(event_start)

    # We get event ends by adding a duration to the start. This way, we
    # prevent that the start and end lists are of different size if an
    # event starts before range_start but ends afterwards.
    if getattr(event, "whole_day", None) or getattr(event, "open_end", None):
        duration = datetime.timedelta(hours=23, minutes=59, seconds=59)
    else:
        event_end = getattr(self.context, "end", None)
        # THIS IS THE PATCH
        if getattr(event, "recurrence", None):
            recurrence_end = datetime.datetime.combine(
                event_start.date(), event_end.time(), event_start.tzinfo
            )
            duration = recurrence_end - event_start
        else:
            duration = event_end - event_start
        # END OF PATCH
    starts = recurrence_sequence_ical(
        event_start,
        recrule=event.recurrence,
        from_=range_start,
        until=range_end,
        duration=duration,
    )

    # XXX potentially occurrence won't need to be wrapped anymore
    # but doing it for backwards compatibility as views/templates
    # still rely on acquisition-wrapped objects.
    def get_obj(start):
        if pydt(event_start.replace(microsecond=0)) == start:
            # If the occurrence date is the same as the event object, the
            # occurrence is the event itself. return it as such.
            # Dates from recurrence_sequence_ical are explicitly without
            # microseconds, while event.start may contain it. So we have to
            # remove it for a valid comparison.
            return self.context
        return Occurrence(
            id=str(start.date()), start=start, end=start + duration
        ).__of__(self.context)

    for start in starts:
        yield get_obj(start)


def _verifyObjectPaste(self, obj, validate_src=True):
    self._old__verifyObjectPaste(obj, validate_src=True)
    portal_type = getattr(aq_base(obj), "portal_type", None)
    constrains = IConstrainTypes(self, None)
    if constrains:
        allowed_ids = [i.getId() for i in constrains.allowedContentTypes()]
        if portal_type not in allowed_ids:
            raise ValueError("Disallowed subobject type: %s" % portal_type)


# PURGE/BAN EVERYTHING (NO TYPE CHECKING)
def isPurged(obj):
    if getRequest() is not None:
        return True


purge.isPurged = isPurged
