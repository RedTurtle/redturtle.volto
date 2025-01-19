"""
Override of the serializer for collections; we only use it to export feeds, so I
consider a complete override of this acceptable.
In redturtle.volto within the summary serializer, the remote URL of links is
requested. The summary serializer it's called on the collection's results items;
If we have a:
plone.app.contentlisting.catalog.CatalogContentListingObject
(the wrapper for collection results on the brain), it's not possible to
calculate the remote URL due to an error when traversing to the
plone_portal_state view. This issue does not occur with the catalog brains.
The CatalogContentListingObject already has the _brain attribute populated.


Let's use that (See later the XXX FIX)
"""

from plone.app.contenttypes.interfaces import ICollection
from plone.restapi.batching import HypermediaBatch
from plone.restapi.deserializer import boolean_value
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.serializer.dxcontent import SerializeToJson
from redturtle.volto.interfaces import IRedturtleVoltoLayer
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.interface import implementer


@implementer(ISerializeToJson)
@adapter(ICollection, IRedturtleVoltoLayer)
class SerializeCollectionToJson(SerializeToJson):
    def __call__(self, version=None, include_items=True):
        result = super().__call__(version=version)

        include_items = self.request.form.get("include_items", include_items)
        include_items = boolean_value(include_items)
        if include_items:
            results = self.context.results(batch=False)
            batch = HypermediaBatch(self.request, results)

            if not self.request.form.get("fullobjects"):
                result["@id"] = batch.canonical_url
            result["items_total"] = batch.items_total
            if batch.links:
                result["batching"] = batch.links

            if "fullobjects" in list(self.request.form):
                result["items"] = [
                    getMultiAdapter(
                        (brain.getObject(), self.request), ISerializeToJson
                    )()
                    for brain in batch
                ]
            else:
                # XXX FIX: use brain._brain instead of brain
                result["items"] = [
                    getMultiAdapter(
                        (brain._brain, self.request), ISerializeToJsonSummary
                    )()
                    for brain in batch
                ]
                # XXX FIX: end

        return result
