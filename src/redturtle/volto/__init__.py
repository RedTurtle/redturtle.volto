# -*- coding: utf-8 -*-
from plone.app.dexterity.behaviors.metadata import ICategorization
from plone.app.dexterity.textindexer import utils
from redturtle.volto import patches  # noqa
from zope.i18nmessageid import MessageFactory


_ = MessageFactory("redturtle.volto")

# Index also subjects in SearchableText.
utils.searchable(ICategorization, "subjects")

import logging
import time
from datetime import datetime

#def formatTime(self, record, datefmt=None):
#    return datetime.fromtimestamp(record.created).astimezone().isoformat(timespec='milliseconds')
#logging.Formatter.formatTime = formatTime
logging.Formatter.converter = time.gmtime
