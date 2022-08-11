# -*- coding: utf-8 -*-
from plone.app.contenttypes.interfaces import IEvent
from plone.dexterity.interfaces import IDexterityContent
from plone.indexer.decorator import indexer
from plone.restapi.interfaces import IBlockSearchableText
from Products.CMFPlone.utils import safe_unicode
from zope.component import adapter
from zope.interface import implementer
from zope.publisher.interfaces.browser import IBrowserRequest


@indexer(IEvent)
def open_end(obj):
    """ """
    return getattr(obj.aq_base, "open_end", False)


@indexer(IEvent)
def whole_day(obj):
    """ """
    return getattr(obj.aq_base, "whole_day", False)


@indexer(IEvent)
def recurrence(obj):
    """ """
    return getattr(obj.aq_base, "recurrence", "")


def _extract_text(block_data):
    result = ""
    for paragraph in block_data.get("blocks", {}):
        text = paragraph["text"]
        result = " ".join((result, text))
    return safe_unicode(result.strip())


@implementer(IBlockSearchableText)
@adapter(IDexterityContent, IBrowserRequest)
class AccordionBlockSearchableText:
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, value):
        text = []
        for subblock in value.get("subblocks", []):
            text.append(_extract_text(subblock.get("text", {})))
            text.append(_extract_text(subblock.get("title", {})))
        return u" ".join([s for s in text])


@implementer(IBlockSearchableText)
@adapter(IDexterityContent, IBrowserRequest)
class AlertBlockSearchableText:
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, value):
        return _extract_text(value.get("text", {}))


@implementer(IBlockSearchableText)
@adapter(IDexterityContent, IBrowserRequest)
class SimpleCardBlockSearchableText:
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, value):
        return " ".join(
            (
                _extract_text(value.get("simple_card_title", {})),
                _extract_text(value.get("simple_card_content", {})),
            )
        )


@implementer(IBlockSearchableText)
@adapter(IDexterityContent, IBrowserRequest)
class CardWithImageBlockSearchableText:
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, value):
        return " ".join(
            (
                _extract_text(value.get("image_card_title", {})),
                _extract_text(value.get("image_card_content", {})),
            )
        )
