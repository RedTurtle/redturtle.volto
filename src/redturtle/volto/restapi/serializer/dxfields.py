# -*- coding: utf-8 -*-
from plone.restapi.serializer.dxfields import DefaultFieldSerializer
from zope.component import adapter
from zope.component import getMultiAdapter
from redturtle.volto.interfaces import IRedturtleVoltoLayer
from plone.app.contenttypes.interfaces import ILink
from zope.schema.interfaces import ITextLine
from plone.app.contenttypes.utils import replace_link_variables_by_paths
from plone.restapi.serializer.converters import json_compatible


@adapter(ITextLine, ILink, IRedturtleVoltoLayer)
class TextLineFieldSerializer(DefaultFieldSerializer):
    def __call__(self):
        if self.field.getName() != "remoteUrl":
            return super(TextLineFieldSerializer, self).__call__()
        import pdb

        pdb.set_trace()
        value = self.get_value()
        path = replace_link_variables_by_paths(context=self.context, url=value)
        portal = getMultiAdapter(
            (self.context, self.context.REQUEST), name="plone_portal_state"
        ).portal()
        ref_obj = portal.restrictedTraverse(path, None)
        if ref_obj:
            value = ref_obj.absolute_url()
        return json_compatible(value)
