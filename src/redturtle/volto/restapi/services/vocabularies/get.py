# -*- coding: utf-8 -*-
from plone import api
from plone.restapi.services.vocabularies.get import VocabulariesGet as BaseGet
from redturtle.volto.interfaces import IRestapiPublicVocabularies
from zope.component import getUtilitiesFor
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse
from zExceptions import Unauthorized

BASIC_ROLES = ["Authenticated", "Member", "Reader"]


@implementer(IPublishTraverse)
class VocabulariesGet(BaseGet):
    def reply(self):
        is_anonymous = api.user.is_anonymous()
        if len(self.params) == 0:
            if is_anonymous:
                raise Unauthorized("Anonymous user can't read vocabularies list.")
            return super(VocabulariesGet, self).reply()
        name = self.params[0]
        allowed_vocabularies = self.get_allowed_vocabularies()

        if name in allowed_vocabularies:
            return super(VocabulariesGet, self).reply()

        if is_anonymous:
            raise Unauthorized("Unable to access {} vocabulary.".format(name))

        roles = api.user.get_roles(user=api.user.get_current(), obj=self.context)
        roles = [x for x in roles if x not in BASIC_ROLES]

        if len(roles) == 0:
            raise Unauthorized("Unable to access {} vocabulary.".format(name))
        return super(VocabulariesGet, self).reply()

    def get_allowed_vocabularies(self):
        utilities = getUtilitiesFor(IRestapiPublicVocabularies)
        data = set()
        for name, vocabs in utilities:
            data.update(vocabs)
        return sorted(list(data))
