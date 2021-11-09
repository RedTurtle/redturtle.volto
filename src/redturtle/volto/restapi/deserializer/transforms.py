from Products.CMFPlone.interfaces import IPloneSiteRoot
from zope.component import adapter
from zope.interface import implementer
from redturtle.volto.interfaces import IRedturtleVoltoLayer
from plone.volto.transforms import NestedResolveUIDDeserializerBase
from plone.restapi.behaviors import IBlocks
from plone.restapi.interfaces import IBlockFieldDeserializationTransformer


class RedturtleNestedResolveUIDDeserializerBase(NestedResolveUIDDeserializerBase):
    def __call__(self, value):
        # bypass plone.volto serialization right now
        return value


@adapter(IBlocks, IRedturtleVoltoLayer)
@implementer(IBlockFieldDeserializationTransformer)
class NestedResolveUIDDeserializer(NestedResolveUIDDeserializerBase):
    """Deserializer for content-types that implements IBlocks behavior"""


@adapter(IPloneSiteRoot, IRedturtleVoltoLayer)
@implementer(IBlockFieldDeserializationTransformer)
class NestedResolveUIDDeserializerRoot(NestedResolveUIDDeserializerBase):
    """Deserializer for site root"""
