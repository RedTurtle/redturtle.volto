# -*- coding: utf-8 -*-
from plone.restapi.interfaces import IIndexQueryParser
from plone.restapi.search.query import (
    ZCTextIndexQueryParser as BaseZCTextIndexQueryParser,
)
from Products.ZCTextIndex.ZCTextIndex import ZCTextIndex
from redturtle.volto.interfaces import IRedturtleVoltoLayer
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface

import re


@implementer(IIndexQueryParser)
@adapter(ZCTextIndex, Interface, IRedturtleVoltoLayer)
class ZCTextIndexQueryParser(BaseZCTextIndexQueryParser):
    def parse_query_value(self, query_value):
        value = super(ZCTextIndexQueryParser, self).parse_query_value(query_value)
        value = re.sub(r"[\([{})\]]|\bnot\b", " ", value)
        return " ".join(value.split())  # remove multiple whitespaces
