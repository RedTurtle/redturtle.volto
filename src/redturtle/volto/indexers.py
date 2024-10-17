# -*- coding: utf-8 -*-
from plone.app.contenttypes.interfaces import IEvent
from plone.dexterity.interfaces import IDexterityContent
from plone.indexer.decorator import indexer
from plone.restapi.indexers import extract_text
from plone.restapi.interfaces import IBlockSearchableText
from zope.component import adapter
from zope.interface import implementer
from zope.publisher.interfaces.browser import IBrowserRequest


try:
    from plone.base.utils import safe_text
except ImportError:
    # Plone5 compatibility
    from Products.CMFPlone.utils import safe_unicode as safe_text


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
    """both slate and draftjs support"""

    if isinstance(block_data, str):
        return block_data

    result = ""
    if isinstance(block_data, dict):
        # draftjs
        for paragraph in block_data.get("blocks", {}):
            text = paragraph["text"]
            result = " ".join((result, text))
    if isinstance(block_data, list):
        result = " ".join(map(recursive_slate_text, block_data))
    return safe_text(result.strip())


def recursive_slate_text(paragraph):
    text = [paragraph.get("text", "")]
    children = paragraph.get("children", {})

    for child in children:
        child_text = recursive_slate_text(paragraph=child)
        if child_text:
            text.append(child_text)
    return "".join(text)


# SearchableText indexers for blocks


class BaseBlockSearchableText:
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, value):
        text = []
        # base fields
        text.append(_extract_text(value.get("text", {})))
        text.append(_extract_text(value.get("title", {})))
        text.append(_extract_text(value.get("description", {})))

        # extra fields
        text.append(self.get_extra_text(value=value))
        text = " ".join(text)
        return safe_text(text.strip())

    def get_extra_text(self, value):
        return ""


@implementer(IBlockSearchableText)
@adapter(IDexterityContent, IBrowserRequest)
class AccordionBlockSearchableText(BaseBlockSearchableText):
    def get_extra_text(self, value):
        text = []
        for subblock in value.get("subblocks", []):
            text.append(_extract_text(subblock.get("text", {})))
            text.append(_extract_text(subblock.get("title", {})))
        return " ".join([s for s in text])


@implementer(IBlockSearchableText)
@adapter(IDexterityContent, IBrowserRequest)
class AlertBlockSearchableText(BaseBlockSearchableText):
    """Alert block"""


@implementer(IBlockSearchableText)
@adapter(IDexterityContent, IBrowserRequest)
class SimpleCardBlockSearchableText(BaseBlockSearchableText):
    def get_extra_text(self, value):
        return " ".join(
            (
                _extract_text(value.get("simple_card_title", {})),
                _extract_text(value.get("simple_card_content", {})),
            )
        )


@implementer(IBlockSearchableText)
@adapter(IDexterityContent, IBrowserRequest)
class CardWithImageBlockSearchableText(BaseBlockSearchableText):
    def get_extra_text(self, value):
        return " ".join(
            (
                _extract_text(value.get("image_card_title", {})),
                _extract_text(value.get("image_card_content", {})),
            )
        )


@implementer(IBlockSearchableText)
@adapter(IDexterityContent, IBrowserRequest)
class CalloutBlockSearchableText(BaseBlockSearchableText):
    """Callout"""


@implementer(IBlockSearchableText)
@adapter(IDexterityContent, IBrowserRequest)
class HeroBlockSearchableText(BaseBlockSearchableText):
    """Hero"""


@implementer(IBlockSearchableText)
@adapter(IDexterityContent, IBrowserRequest)
class CTABlockSearchableText(BaseBlockSearchableText):
    """Call to action block"""

    def get_extra_text(self, value):
        return " ".join(
            (
                _extract_text(value.get("cta_title", {})),
                _extract_text(value.get("cta_content", {})),
            )
        )


@implementer(IBlockSearchableText)
@adapter(IDexterityContent, IBrowserRequest)
class GridBlockSearchableText(BaseBlockSearchableText):
    """grid block"""

    def get_extra_text(self, value):
        blocks_text = []
        for block in value.get("blocks", {}).values():
            blocks_text.append(
                extract_text(block=block, obj=self.context, request=self.request)
            )
        return " ".join(blocks_text)


@implementer(IBlockSearchableText)
@adapter(IDexterityContent, IBrowserRequest)
class SlateTableBlockSearchableText(BaseBlockSearchableText):
    """slate table"""

    def get_extra_text(self, value):
        table_text = []
        for row in value.get("table", {}).get("rows", []):
            for cell in row.get("cells", []):
                table_text.append(_extract_text(cell.get("value", {})))

        return " ".join(table_text)


@implementer(IBlockSearchableText)
@adapter(IDexterityContent, IBrowserRequest)
class ContactsBlockSearchableText(BaseBlockSearchableText):
    """contacts"""

    def get_extra_text(self, value):
        text = []
        for subblock in value.get("subblocks", []):
            text.append(_extract_text(subblock.get("text", {})))
            text.append(_extract_text(subblock.get("title", {})))
            text.append(_extract_text(subblock.get("tel", {})))
            text.append(_extract_text(subblock.get("email", {})))
        return " ".join([s for s in text])


@implementer(IBlockSearchableText)
@adapter(IDexterityContent, IBrowserRequest)
class IconBlockSearchableText(BaseBlockSearchableText):
    """icons"""

    def get_extra_text(self, value):
        text = []
        for subblock in value.get("subblocks", []):
            text.append(_extract_text(subblock.get("text", {})))
            text.append(_extract_text(subblock.get("title", {})))
        return " ".join([s for s in text])


@implementer(IBlockSearchableText)
@adapter(IDexterityContent, IBrowserRequest)
class NumbersBlockSearchableText(BaseBlockSearchableText):
    """numbers"""

    def get_extra_text(self, value):
        text = []
        for subblock in value.get("subblocks", []):
            text.append(_extract_text(subblock.get("text", {})))
            text.append(_extract_text(subblock.get("title", {})))
        return " ".join([s for s in text])


@implementer(IBlockSearchableText)
@adapter(IDexterityContent, IBrowserRequest)
class RemoteCounterBlockSearchableText(BaseBlockSearchableText):
    """reomte counter"""


@implementer(IBlockSearchableText)
@adapter(IDexterityContent, IBrowserRequest)
class CountDownBlockSearchableText(BaseBlockSearchableText):
    """count-down block"""

    def get_extra_text(self, value):
        return " ".join((_extract_text(value.get("countdown_text", {})),))
