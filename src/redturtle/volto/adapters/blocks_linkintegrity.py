from collective.volto.blocksfield.field import BlocksField
from plone.app.linkintegrity.interfaces import IRetriever
from plone.app.linkintegrity.parser import extractLinks
from plone.app.textfield import RichText
from plone.dexterity.interfaces import IDexterityContainer
from plone.dexterity.interfaces import IDexterityContent
from plone.dexterity.interfaces import IDexterityFTI
from plone.dexterity.interfaces import IDexterityItem
from plone.dexterity.utils import getAdditionalSchemata
from plone.restapi.blocks import iter_block_transform_handlers
from plone.restapi.blocks import visit_blocks
from plone.restapi.blocks_linkintegrity import BlocksRetriever as BaseBlocksRetriever
from plone.restapi.blocks_linkintegrity import (
    GenericBlockLinksRetriever as BaseGenericBlockLinksRetriever,
)
from plone.restapi.blocks_linkintegrity import (
    SlateBlockLinksRetriever as BaseSlateBlockLinksRetriever,
)
from plone.restapi.blocks_linkintegrity import (
    TextBlockLinksRetriever as BaseTextBlockLinksRetriever,
)
from plone.restapi.interfaces import IBlockFieldLinkIntegrityRetriever
from redturtle.volto.interfaces import IRedturtleVoltoLayer
from zope.component import adapter
from zope.component import getUtility
from zope.interface import implementer
from zope.schema import getFieldsInOrder


class BaseRTRetriever(BaseBlocksRetriever):
    def retrieveLinks(self):
        """
        Check links in:
        - blocks field
        - text fields
        - BlocksField fields
        """
        # first do plone.restapi links generation
        links = super().retrieveLinks()

        # then iterate over content schema and check for other references
        fti = getUtility(IDexterityFTI, name=self.context.portal_type)
        schema = fti.lookupSchema()
        additional_schema = getAdditionalSchemata(
            context=self.context, portal_type=self.context.portal_type
        )
        schemas = [i for i in additional_schema] + [schema]
        links = set()
        for schema in schemas:
            for name, field in getFieldsInOrder(schema):
                if isinstance(field, RichText):
                    value = getattr(schema(self.context), name)
                    if not value or not getattr(value, "raw", None):
                        continue
                    links |= set(extractLinks(value.raw))
                elif isinstance(field, BlocksField):
                    value = field.get(self.context)
                    if not value:
                        continue
                    if not isinstance(value, dict):
                        continue
                    blocks = value.get("blocks", {})
                    if not blocks:
                        continue
                    for block in visit_blocks(self.context, blocks):
                        for handler in iter_block_transform_handlers(
                            self.context, block, IBlockFieldLinkIntegrityRetriever
                        ):
                            links |= set(handler(block))
        return links


@implementer(IRetriever)
@adapter(IDexterityItem)
class BlocksRetrieverItem(BaseRTRetriever):
    """
    Retriever for Item contents.
    Needed a more specific than IDexterityContent because it's already registered.
    """


@implementer(IRetriever)
@adapter(IDexterityContainer)
class BlocksRetrieverContainer(BaseRTRetriever):
    """
    Retriever for Container contents.
    Needed a more specific than IDexterityContent because it's already registered.
    """


@adapter(IDexterityContent, IRedturtleVoltoLayer)
@implementer(IBlockFieldLinkIntegrityRetriever)
class TextBlockLinksRetriever(BaseTextBlockLinksRetriever):
    """Retriever for text blocks"""


@adapter(IDexterityContent, IRedturtleVoltoLayer)
@implementer(IBlockFieldLinkIntegrityRetriever)
class SlateBlockLinksRetriever(BaseSlateBlockLinksRetriever):
    """Retriever for slate blocks"""


@adapter(IDexterityContent, IRedturtleVoltoLayer)
@implementer(IBlockFieldLinkIntegrityRetriever)
class GenericBlockLinksRetriever(BaseGenericBlockLinksRetriever):
    """Retriever for generic blocks"""
