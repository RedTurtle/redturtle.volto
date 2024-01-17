from BTrees.IIBTree import difference
from BTrees.IIBTree import IISet
from plone.event.interfaces import IEventRecurrence
from plone.event.interfaces import IRecurrenceSupport
from plone.event.recurrence import recurrence_sequence_ical
from plone.event.utils import dt2int
from plone.event.utils import pydt
from Products.DateRecurringIndex.index import DateRecurringIndex
from Products.DateRecurringIndex.index import IDateRecurringIndex
from Products.DateRecurringIndex.index import _marker
from Products.PluginIndexes.util import safe_callable
from ZODB.POSException import ConflictError
from zope.interface import implementer
from zope.schema import Text
from App.special_dtml import DTMLFile


class IDateRangeRecurringIndex(IDateRecurringIndex):
    attr_start = Text(title="Attribute- or fieldname of start date (optional).")


@implementer(IDateRangeRecurringIndex)
class DateRangeRecurringIndex(DateRecurringIndex):
    meta_type = "DateRangeRecurringIndex"

    def __init__(self, id, ignore_ex=None, call_methods=None, extra=None, caller=None):
        """Initialize the index
        @ param extra.recurdef:
        @ param extral.until:
        """
        super().__init__(id, ignore_ex, call_methods, extra, caller)
        self.attr_start = extra.start

    def index_object(self, documentId, obj, threshold=None):
        """index an object, normalizing the indexed value to an integer

        o Normalized value has granularity of one minute.

        o Objects which have 'None' as indexed value are *omitted*,
          by design.

        o Repeat by recurdef - a RFC2445 reccurence definition string

        COPIED FROM the original one.
        """
        returnStatus = 0

        try:
            date_attr = getattr(obj, self.id)
            if safe_callable(date_attr):
                date_attr = date_attr()
        except AttributeError:
            return returnStatus

        recurdef = getattr(obj, self.attr_recurdef, None)
        if safe_callable(recurdef):
            recurdef = recurdef()

        if not recurdef:
            dates = [pydt(date_attr)]
        else:
            until = getattr(obj, self.attr_until, None)
            start = getattr(obj, self.attr_start, None)
            if safe_callable(until):
                until = until()
            # THIS IS THE PATCH
            if not start:
                # This index is the start of the date range, and the index has not attr_start set
                # Calculate recurrence sequence base on current date value.
                dates = recurrence_sequence_ical(
                    date_attr, recrule=recurdef, until=until
                )
            else:
                # This index is the end of the recurrence and need to be calculated like p.a.events calculates occurences.
                # Base DateRecurringIndex appends recrule to end index, but it's not correct because
                # if the rrule is "once a week for 5 times", the end should be calculated starting from the start attr and not from the end one.
                if IEventRecurrence.providedBy(obj):
                    occ_list = list(
                        IRecurrenceSupport(obj._getWrappedObject()).occurrences()
                    )
                    dates = [x.end for x in occ_list]
        newvalues = IISet(map(dt2int, dates))
        oldvalues = self._unindex.get(documentId, _marker)
        if oldvalues is not _marker:
            oldvalues = IISet(oldvalues)

        if (
            oldvalues is not _marker
            and newvalues is not _marker
            and not difference(newvalues, oldvalues)
            and not difference(oldvalues, newvalues)
        ):
            # difference is calculated relative to first argument, so we have
            # to use it twice here
            return returnStatus

        if oldvalues is not _marker:
            for oldvalue in oldvalues:
                self.removeForwardIndexEntry(oldvalue, documentId)
            if newvalues is _marker:
                try:
                    del self._unindex[documentId]
                except ConflictError:
                    raise
                except Exception:
                    LOG.error(
                        "Should not happen: oldvalues was there,"
                        " now it's not, for document with id %s" % documentId
                    )

        if newvalues is not _marker:
            inserted = False
            for value in newvalues:
                self.insertForwardIndexEntry(value, documentId)
                inserted = True
            if inserted:
                # store tuple values in reverse index entries for sorting
                self._unindex[documentId] = tuple(newvalues)
                returnStatus = 1

        if returnStatus > 0:
            self._increment_counter()

        return returnStatus


manage_addDRRIndexForm = DTMLFile("www/addDRRIndex", globals())


def manage_addDRRIndex(self, id, extra=None, REQUEST=None, RESPONSE=None, URL3=None):
    """Add a DateRangeRecurringIndex"""
    return self.manage_addIndex(
        id,
        "DateRangeRecurringIndex",
        extra=extra,
        REQUEST=REQUEST,
        RESPONSE=RESPONSE,
        URL1=URL3,
    )
