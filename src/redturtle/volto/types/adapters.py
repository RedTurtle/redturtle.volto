# -*- coding: utf-8 -*-
"""JsonSchema providers."""
from plone.app.textfield.interfaces import IRichText
from plone.restapi.types.interfaces import IJsonSchemaProvider
from plone.restapi.types.utils import get_fieldsets
from plone.restapi.types.utils import get_jsonschema_properties
from plone.restapi.types.utils import get_querysource_url
from plone.restapi.types.utils import get_source_url
from plone.restapi.types.utils import get_vocabulary_url
from plone.restapi.types.utils import get_widget_params
from plone.schema import IEmail
from plone.schema import IJSONField
from z3c.formwidget.query.interfaces import IQuerySource
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.i18n import translate
from zope.interface import implementer
from zope.interface import Interface
from zope.schema.interfaces import IASCII
from zope.schema.interfaces import IASCIILine
from zope.schema.interfaces import IBool
from zope.schema.interfaces import IBytes
from zope.schema.interfaces import IChoice
from zope.schema.interfaces import ICollection
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.interfaces import IDate
from zope.schema.interfaces import IDatetime
from zope.schema.interfaces import IDecimal
from zope.schema.interfaces import IDict
from zope.schema.interfaces import IField
from zope.schema.interfaces import IFloat
from zope.schema.interfaces import IInt
from zope.schema.interfaces import IList
from zope.schema.interfaces import IObject
from zope.schema.interfaces import IPassword
from zope.schema.interfaces import IURI
from zope.schema.interfaces import ISet
from zope.schema.interfaces import IText
from zope.schema.interfaces import ITextLine
from zope.schema.interfaces import ITuple
from plone.app.contenttypes.interfaces import ILink
from redturtle.volto.interfaces import IRedturtleVoltoLayer
from plone.restapi.types.adapters import TextLineJsonSchemaProvider as Base


@adapter(ITextLine, Interface, IRedturtleVoltoLayer)
@implementer(IJsonSchemaProvider)
class TextLineJsonSchemaProvider(Base):
    def get_widget(self):
        if self.field.__name__ == "remoteUrl":
            return "url"
        return super(TextLineJsonSchemaProvider, self).get_widget()
