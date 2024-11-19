from plone.dexterity.interfaces import IDexterityContent
from plone.restapi.blocks_linkintegrity import (
    GenericBlockLinksRetriever as BaseGenericBlockLinksRetriever,
)
from plone.restapi.blocks_linkintegrity import SlateBlockLinksRetriever
from plone.restapi.blocks_linkintegrity import (
    TextBlockLinksRetriever as BaseTextBlockLinksRetriever,
)
from plone.restapi.deserializer.blocks import iterate_children
from plone.restapi.interfaces import IBlockFieldLinkIntegrityRetriever
from redturtle.volto.interfaces import IRedturtleVoltoLayer
from zope.component import adapter
from zope.interface import implementer
from zope.publisher.interfaces.browser import IBrowserRequest


def get_urls_from_value(value):
    """Generator of urls from a block field value

    Recognizes:
    - strings containing "resolveuid"
    - objects with an @id property containing "resolveuid"
    - objects with an UID property
    - lists of either of the above
    """
    if isinstance(value, str) and "resolveuid" in value:
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from get_urls_from_value(item)
    elif isinstance(value, dict):
        uid = value.get("UID", "")
        if uid:
            yield f"resolveuid/{uid}"
        else:
            yield from get_urls_from_value(value.get("@id"))


class SubBlocksRetriever(SlateBlockLinksRetriever):

    def extract_links(self, block_data):
        children = iterate_children(block_data or [])
        for child in children:
            node_type = child.get("type")
            if node_type:
                handler = getattr(self, f"handle_{node_type}", None)
                if handler:
                    value = handler(child)
                    if value:
                        self.links.append(value)


# Specific blocks adapters
@adapter(IDexterityContent, IRedturtleVoltoLayer)
@implementer(IBlockFieldLinkIntegrityRetriever)
class TextBlockLinksRetriever(BaseTextBlockLinksRetriever):
    """Retriever for text blocks"""


@adapter(IDexterityContent, IRedturtleVoltoLayer)
@implementer(IBlockFieldLinkIntegrityRetriever)
class RTSlateBlockLinksRetriever(SlateBlockLinksRetriever):
    """Retriever for slate blocks"""


@adapter(IDexterityContent, IRedturtleVoltoLayer)
@implementer(IBlockFieldLinkIntegrityRetriever)
class GenericBlockLinksRetriever(BaseGenericBlockLinksRetriever):
    """Retriever for generic blocks"""

    def __call__(self, block):
        """
        The customization is the list of field names.
        """
        links = []
        for field in [
            "url",
            "href",
            "preview_image",
            "linkHref",
            "linkMore",
            "moreHref",
            "background",
            "audio",
            "linkHrefColumn",
            "ctaLink",
        ]:
            value = block.get(field, "")
            if value:
                for url in get_urls_from_value(value):
                    links.append(url)
        return links


@adapter(IDexterityContent, IBrowserRequest)
@implementer(IBlockFieldLinkIntegrityRetriever)
class SimpleCardBlockLinksRetriever(SlateBlockLinksRetriever):
    order = 200
    block_type = "testo_riquadro_semplice"
    field = "simple_card_content"


@adapter(IDexterityContent, IBrowserRequest)
@implementer(IBlockFieldLinkIntegrityRetriever)
class AccordionBlockLinksRetriever(SubBlocksRetriever):
    order = 200
    block_type = "accordion"

    def __call__(self, block):
        if not block:
            return self.links
        description = block.get("description", [])
        self.extract_links(block_data=description)

        for subblock in block.get("subblocks", []):
            self.extract_links(block_data=subblock.get("text", {}))
            for url in get_urls_from_value(subblock.get("href", "")):
                self.links.append(url)
        return self.links


@adapter(IDexterityContent, IBrowserRequest)
@implementer(IBlockFieldLinkIntegrityRetriever)
class AlertBlockLinksRetriever(SlateBlockLinksRetriever):
    order = 200
    block_type = "alert"
    field = "text"


@adapter(IDexterityContent, IBrowserRequest)
@implementer(IBlockFieldLinkIntegrityRetriever)
class ImageCardBlockLinksRetriever(SlateBlockLinksRetriever):
    order = 200
    block_type = "testo_riquadro_immagine"
    field = "image_card_content"


@adapter(IDexterityContent, IBrowserRequest)
@implementer(IBlockFieldLinkIntegrityRetriever)
class CalloutBlockLinksRetriever(SlateBlockLinksRetriever):
    order = 200
    block_type = "callout_block"
    field = "text"


@adapter(IDexterityContent, IBrowserRequest)
@implementer(IBlockFieldLinkIntegrityRetriever)
class CTABlockLinksRetriever(SlateBlockLinksRetriever):
    order = 200
    block_type = "cta_block"
    field = "cta_content"

    def __call__(self, block):
        super().__call__(block=block)

        for image_uid in block.get("ctaImage", []):
            self.links.append(f"resolveuid/{image_uid}")
        return self.links


@adapter(IDexterityContent, IBrowserRequest)
@implementer(IBlockFieldLinkIntegrityRetriever)
class TableBlockLinksRetriever(SubBlocksRetriever):
    order = 200
    block_type = "slateTable"

    def __call__(self, block):
        if not block:
            return self.links

        for row in block.get("table", {}).get("rows", []):
            for cell in row.get("cells", []):

                self.extract_links(block_data=cell.get("value", {}))

        return self.links


@adapter(IDexterityContent, IBrowserRequest)
@implementer(IBlockFieldLinkIntegrityRetriever)
class ContactsBlockLinksRetriever(SubBlocksRetriever):
    order = 200
    block_type = "contacts"

    def __call__(self, block):
        if not block:
            return self.links
        description = block.get("description", [])
        self.extract_links(block_data=description)

        for subblock in block.get("subblocks", []):
            self.extract_links(block_data=subblock.get("text", {}))
            self.extract_links(block_data=subblock.get("tel", {}))
            self.extract_links(block_data=subblock.get("email", {}))

        return self.links


@adapter(IDexterityContent, IBrowserRequest)
@implementer(IBlockFieldLinkIntegrityRetriever)
class IconBlockLinksRetriever(SubBlocksRetriever):
    order = 200
    block_type = "iconBlocks"

    def __call__(self, block):
        if not block:
            return self.links
        description = block.get("description", [])
        self.extract_links(block_data=description)

        for img in block.get("background", []):
            # this is not standard, is a list of uids, no a list of objects with UID key
            self.links.append(f"resolveuid/{img}")

        for subblock in block.get("subblocks", []):
            self.extract_links(block_data=subblock.get("text", {}))
            for url in get_urls_from_value(subblock.get("href", "")):
                self.links.append(url)

        return self.links
