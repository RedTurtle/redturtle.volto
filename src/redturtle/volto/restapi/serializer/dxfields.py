# -*- coding: utf-8 -*-
from plone.app.contenttypes.interfaces import ILink
from plone.app.contenttypes.utils import replace_link_variables_by_paths
from plone.outputfilters.browser.resolveuid import uuidToURL
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.serializer.dxfields import DefaultFieldSerializer
from redturtle.volto.interfaces import IRedturtleVoltoLayer
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.schema.interfaces import ITextLine
from AccessControl import getSecurityManager
from Products.CMFCore.permissions import ModifyPortalContent
from plone.app.contenttypes.interfaces import ILink
from plone.app.contenttypes.utils import replace_link_variables_by_paths
from plone.app.textfield.interfaces import IRichText
from plone.dexterity.interfaces import IDexterityContent
from plone.namedfile.interfaces import INamedFileField
from plone.namedfile.interfaces import INamedImageField
from plone.restapi.imaging import get_original_image_url
from plone.restapi.imaging import get_scales
from plone.restapi.interfaces import IFieldSerializer
from plone.restapi.interfaces import IPrimaryFieldTarget
from plone.restapi.serializer.converters import json_compatible
from zope.component import getMultiAdapter
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface
from zope.schema.interfaces import IChoice
from zope.schema.interfaces import ICollection
from zope.schema.interfaces import IField
from zope.schema.interfaces import ITextLine
from zope.schema.interfaces import IVocabularyTokenized
from zope.schema.interfaces import IDatetime
from plone.app.dexterity.behaviors.metadata import IPublication

import re

RESOLVEUID_RE = re.compile(".*?/resolve[Uu]id/([^/]*)/?(.*)$")


@adapter(ITextLine, ILink, IRedturtleVoltoLayer)
class TextLineFieldSerializer(DefaultFieldSerializer):
    def __call__(self):
        if self.field.getName() != "remoteUrl":
            return super(TextLineFieldSerializer, self).__call__()
        value = self.get_value()

        path = replace_link_variables_by_paths(context=self.context, url=value)
        match = RESOLVEUID_RE.match(path)
        if match:
            uid, suffix = match.groups()
            value = uuidToURL(uid)
        else:
            portal = getMultiAdapter(
                (self.context, self.context.REQUEST), name="plone_portal_state"
            ).portal()
            ref_obj = portal.restrictedTraverse(path, None)
            if ref_obj:
                value = ref_obj.absolute_url()

        return json_compatible(value)


@adapter(IDatetime, IDexterityContent, IRedturtleVoltoLayer)
@implementer(IFieldSerializer)
class DateTimeFieldSerializer:
    def __init__(self, field, context, request):
        self.context = context
        self.request = request
        self.field = field

    def __call__(self):
        return json_compatible(self.get_value())

    def get_value(self, default=None):
        value = getattr(
            self.field.interface(self.context), self.field.__name__, default
        )
        if value and self.field.interface == IPublication:
            # the patch: we want the dates with full tz infos
            # value is taken from
            # plone.app.dexterity.behaviors.metadata.Publication and escape
            # the timezone
            return getattr(self.context, self.field.__name__)()
        return value
