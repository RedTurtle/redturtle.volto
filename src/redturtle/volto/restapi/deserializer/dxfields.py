# -*- coding: utf-8 -*-
from plone.app.contenttypes.interfaces import ILink
from plone.app.event.base import default_timezone
from plone.app.textfield.interfaces import IRichText
from plone.dexterity.interfaces import IDexterityContent
from plone.restapi.deserializer.blocks import path2uid
from plone.restapi.deserializer.dxfields import (
    DatetimeFieldDeserializer as DefaultDatetimeFieldDeserializer,
    RichTextFieldDeserializer as BaseRichTextDeserializer,
    TextLineFieldDeserializer as BaseTextLineDeserializer,
)
from plone.restapi.interfaces import IFieldDeserializer
from Products.CMFPlone.utils import safe_unicode
from pytz import timezone
from pytz import utc
from redturtle.volto.interfaces import IRedturtleVoltoLayer
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.interface import implementer
from zope.schema.interfaces import IDatetime
from zope.schema.interfaces import ITextLine

import pytz
import dateutil
import lxml


@implementer(IFieldDeserializer)
@adapter(IRichText, IDexterityContent, IRedturtleVoltoLayer)
class RichTextFieldDeserializer(BaseRichTextDeserializer):
    def __call__(self, value):
        if value:
            if isinstance(value, dict):
                html = value.get("data", u"")
                if html:
                    value["data"] = self.convert_internal_links(html=html)
            else:
                value = self.convert_internal_links(html=value)
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


@implementer(IFieldDeserializer)
@adapter(ITextLine, ILink, IRedturtleVoltoLayer)
class LinkTextLineFieldDeserializer(BaseTextLineDeserializer):
    def __call__(self, value):
        value = super(LinkTextLineFieldDeserializer, self).__call__(value)
        if self.field.getName() == "remoteUrl":
            portal = getMultiAdapter(
                (self.context, self.context.REQUEST), name="plone_portal_state"
            ).portal()

            transformed_url = path2uid(context=portal, link=value)
            if transformed_url != value and "resolveuid" in transformed_url:
                value = "${{portal_url}}/{uid}".format(uid=transformed_url)
        return value


@implementer(IFieldDeserializer)
@adapter(IDatetime, IDexterityContent, IRedturtleVoltoLayer)
class DatetimeFieldDeserializer(DefaultDatetimeFieldDeserializer):
    def __call__(self, value):
        """
        Always set current timezone and ignore stored one.
        """
        if value is None:
            self.field.validate(value)
            return

        tzinfo = pytz.timezone(default_timezone())

        # Parse ISO 8601 string with dateutil
        try:
            dt = dateutil.parser.parse(value)
        except ValueError:
            raise ValueError(u"Invalid date: {}".format(value))

        # Convert to TZ aware in UTC
        if dt.tzinfo is not None:
            dt = dt.astimezone(utc)
        else:
            dt = utc.localize(dt)

        # Convert to local TZ aware or naive UTC
        if tzinfo is not None:
            tz = timezone(tzinfo.zone)
            value = tz.normalize(dt.astimezone(tz))
        else:
            value = utc.normalize(dt.astimezone(utc)).replace(tzinfo=None)

        self.field.validate(value)
        return value
