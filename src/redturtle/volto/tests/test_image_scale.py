from DateTime import DateTime
from OFS.SimpleItem import SimpleItem
from plone.app.contenttypes.interfaces import IImage
from plone.namedfile.scaling import ImageScaling
from plone.namedfile.tests.test_scaling import DummyContent
from plone.namedfile.tests.test_scaling import getFile
from plone.namedfile.tests.test_scaling import MockNamedImage
from redturtle.volto.testing import REDTURTLE_VOLTO_API_FUNCTIONAL_TESTING
from zope.annotation import IAttributeAnnotatable
from zope.interface import implementer

import unittest


@implementer(IAttributeAnnotatable, IImage)  # IHasImage)
class DummyContent(SimpleItem):
    image = None
    modified = DateTime
    id = __name__ = "item"
    title = "foo"

    def Title(self):
        return self.title

    def UID(self):
        return "dummy_uuid"


class TestPublicationFieldsFixes(unittest.TestCase):

    layer = REDTURTLE_VOLTO_API_FUNCTIONAL_TESTING

    def setUp(self):
        data = getFile("image.png")
        item = DummyContent()
        item.image = MockNamedImage(data, "image/png", "image.png")
        self.layer["app"]._setOb("item", item)
        self.item = self.layer["app"].item
        self._orig_sizes = ImageScaling._sizes
        self.scaling = ImageScaling(self.item, None)

    def tearDown(self):
        ImageScaling._sizes = self._orig_sizes

    def test_image_prescale(self):
        self.scaling.available_sizes = {"foo": (60, 60)}
        foo = self.scaling.scale("image", scale="foo", pre=True)
        tag = foo.tag()
        self.assertRegexpMatches(tag, r'<img src="http://[^/]+/item/@@images/image-60-[a-z0-9]+.png" alt="foo" title="foo" height="60" width="60" />')
