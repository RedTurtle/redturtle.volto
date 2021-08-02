# -*- coding: utf-8 -*-
from DateTime import DateTime
from plone.restapi.interfaces import IDeserializeFromJson
from Products.CMFCore.interfaces import IFolderish
from zope.component import queryMultiAdapter
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse
from plone.restapi.services.workflow.transition import (
    WorkflowTransition as BaseService,
)


@implementer(IPublishTraverse)
class WorkflowTransition(BaseService):
    def recurse_transition(
        self, objs, comment, publication_dates, include_children=False
    ):
        for obj in objs:
            if publication_dates:
                deserializer = queryMultiAdapter(
                    (obj, self.request), IDeserializeFromJson
                )
                deserializer(data=publication_dates)

            if obj.EffectiveDate() == "None":
                obj.setEffectiveDate(DateTime())
                obj.reindexObject()
            # patch: https://github.com/plone/plone.restapi/pull/1190
            if not self.wftool.getWorkflowsFor(obj):
                continue
            # end of patch
            self.wftool.doActionFor(obj, self.transition, comment=comment)
            if include_children and IFolderish.providedBy(obj):
                self.recurse_transition(
                    obj.objectValues(),
                    comment,
                    publication_dates,
                    include_children,
                )
