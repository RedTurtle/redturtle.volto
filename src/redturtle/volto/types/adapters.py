# -*- coding: utf-8 -*-
"""JsonSchema providers."""
from plone.restapi.types.adapters import TextLineJsonSchemaProvider as Base
from plone.restapi.types.interfaces import IJsonSchemaProvider
from redturtle.volto.interfaces import IRedturtleVoltoLayer
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface
from zope.schema.interfaces import ITextLine
from zope.i18n import translate
from redturtle.volto import _


@adapter(ITextLine, Interface, IRedturtleVoltoLayer)
@implementer(IJsonSchemaProvider)
class TextLineJsonSchemaProvider(Base):
    def get_widget(self):
        if self.field.__name__ == "remoteUrl":
            return "url"
        return super(TextLineJsonSchemaProvider, self).get_widget()

    def get_description(self):
        if self.field.__name__ == "remoteUrl":
            return translate(
                _(
                    "remoteUrl_restapi_label",
                    default="Insert an external link directly into the field,"
                    "or select an internal link clicking on the icon.",
                ),
                context=self.request,
            )
        return super(TextLineJsonSchemaProvider, self).get_description()
