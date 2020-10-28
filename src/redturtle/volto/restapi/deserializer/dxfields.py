# -*- coding: utf-8 -*-
from plone.app.textfield.interfaces import IRichText
from plone.dexterity.interfaces import IDexterityContent
from plone.restapi.interfaces import IFieldDeserializer
from plone.restapi.deserializer.blocks import path2uid
from plone.restapi.deserializer.dxfields import (
    RichTextFieldDeserializer as BaseDeserializer,
)
from Products.CMFPlone.utils import safe_unicode
from zope.component import adapter
from zope.interface import implementer
from redturtle.volto.interfaces import IRedturtleVoltoLayer

import lxml


@implementer(IFieldDeserializer)
@adapter(IRichText, IDexterityContent, IRedturtleVoltoLayer)
class RichTextFieldDeserializer(BaseDeserializer):
    def __call__(self, value):
        html = value.get("data", u"")
        if html:
            value["data"] = self.convert_internal_links(html=html)
        return super(RichTextFieldDeserializer, self).__call__(value=value)

    def convert_internal_links(self, html):
        root = lxml.html.fromstring(html)

        # fix links
        for link in root.xpath("//a"):
            link.set(
                "href", path2uid(context=self.context, link=link.get("href"))
            )

        # fix image src
        for img in root.xpath("//img"):
            img.set("src", path2uid(context=self.context, link=img.get("src")))

        return safe_unicode(lxml.html.tostring(root))
