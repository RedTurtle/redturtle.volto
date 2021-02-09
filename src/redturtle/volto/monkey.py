# -*- coding: utf-8 -*-
from Products.CMFPlone.interfaces import IFilterSchema
from Products.CMFPlone.utils import safe_encode
from Products.PortalTransforms.libtransforms.utils import bodyfinder
from lxml import etree
from lxml import html
from lxml.html.clean import Cleaner
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from Products.PortalTransforms.transforms.safe_html import hasScript

import six


def scrub_html(self, orig):
    # append html tag to create a dummy parent for the tree
    html_parser = html.HTMLParser(encoding="utf-8")
    orig = safe_encode(orig)
    tag = b"<html"
    if tag in orig.lower():
        # full html
        tree = html.fromstring(orig, parser=html_parser)
        strip_outer = bodyfinder
    else:
        # partial html (i.e. coming from WYSIWYG editor)
        tree = html.fragment_fromstring(
            orig, create_parent=True, parser=html_parser
        )

        def strip_outer(s):
            return s[5:-6]

    for elem in tree.iter(etree.Element):
        if elem is not None:
            for attrib, value in elem.attrib.items():
                if hasScript(value):
                    del elem.attrib[attrib]

    registry = getUtility(IRegistry)
    self.settings = registry.forInterface(IFilterSchema, prefix="plone")

    valid_tags = self.settings.valid_tags
    nasty_tags = [t for t in self.settings.nasty_tags if t not in valid_tags]
    if six.PY2:
        safe_attrs = [attr.decode() for attr in html.defs.safe_attrs]
    else:
        safe_attrs = [i for i in html.defs.safe_attrs]
    safe_attrs.extend(self.settings.custom_attributes)
    remove_script = "script" in nasty_tags and 1 or 0
    cleaner = Cleaner(
        kill_tags=nasty_tags,
        remove_tags=[],
        allow_tags=valid_tags,
        page_structure=False,
        safe_attrs_only=True,
        safe_attrs=safe_attrs,
        embedded=False,
        remove_unknown_tags=False,
        meta=False,
        javascript=remove_script,
        scripts=remove_script,
        forms=False,
        style=False,
    )
    try:
        cleaner(tree)
    except AssertionError:
        # some VERY invalid HTML
        return ""
    # remove all except body or outer div
    # changes in
    # https://github.com/plone/Products.PortalTransforms/pull/43
    if six.PY2:
        result = etree.tostring(tree, encoding="utf-8", method="html").strip()
    else:
        result = etree.tounicode(tree, method="html").strip()
    return strip_outer(result)
