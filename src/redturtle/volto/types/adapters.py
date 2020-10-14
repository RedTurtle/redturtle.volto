# -*- coding: utf-8 -*-
"""JsonSchema providers."""
from plone.restapi.types.adapters import TextLineJsonSchemaProvider as Base
from plone.restapi.types.interfaces import IJsonSchemaProvider
from redturtle.volto.interfaces import IRedturtleVoltoLayer
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface
from zope.schema.interfaces import ITextLine


@adapter(ITextLine, Interface, IRedturtleVoltoLayer)
@implementer(IJsonSchemaProvider)
class TextLineJsonSchemaProvider(Base):
    def get_widget(self):
        if self.field.__name__ == "remoteUrl":
            return "url"
        return super(TextLineJsonSchemaProvider, self).get_widget()
