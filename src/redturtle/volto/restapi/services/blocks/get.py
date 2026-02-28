# -*- coding: utf-8 -*-
from plone.dexterity.interfaces import IDexterityContainer
from plone.restapi.services import Service
from zope.component import adapter
from zope.interface import Interface
from plone import api
from plone.restapi.interfaces import ISerializeToJson
from zope.component import getMultiAdapter
import json

# @adapter(IDexterityContainer, Interface)
# class BlocksHandler(object):
#     def __init__(self, context, request):
#         self.context = context
#         self.request = request

#     def __call__(self):
#         import pdb;pdb.set_trace()

#         catalog = api.portal.get_tool("portal_catalog")
#         zcatalog = catalog._catalog

#         blocks_index = zcatalog.getIndex("block_types")
#         data_indexed = blocks_index._index

#         results = {}

#         for docids in data_indexed.values():
#             for docid in docids:
#                 zcinfo = zcatalog.getIndexDataForRID(docid)
#                 for btype in zcinfo.get("block_types", []):
#                     tmp_list = results.get(btype, [])
#                     brain_path = zcinfo.get("path", "")
#                     if brain_path not in tmp_list:
#                         tmp_list.append(brain_path)

#                     results.update({btype: tmp_list})

#         import pdb;pdb.set_trace()

#         #results = getMultiAdapter((results, self.request), ISerializeToJson)()
#         return results
    
#         # for key, value in data_indexed.iteritems():
#         #     for item in value.values():
#         #         pass
#         #     #results.update(key: "")


#         # brains = catalog(index="block_types")
#         # if not brains:
#         #     return

#         # for brain in brains:



class BlocksGet(Service):
    def reply(self):
        catalog = api.portal.get_tool("portal_catalog")
        zcatalog = catalog._catalog

        blocks_index = zcatalog.getIndex("block_types")
        data_indexed = blocks_index._index

        results = {}

        for docids in data_indexed.values():
            for docid in docids:
                zcinfo = zcatalog.getIndexDataForRID(docid)
                for btype in zcinfo.get("block_types", []):
                    tmp_list = results.get(btype, [])
                    brain_path = zcinfo.get("path", "")
                    if brain_path not in tmp_list:
                        tmp_list.append(brain_path)

                    results.update({btype: tmp_list})

        return json.dumps(results)
    
