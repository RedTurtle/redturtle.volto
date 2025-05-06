from zope.interface import implementer
from zope.schema.interfaces import IVocabularyFactory
from plone.app.vocabularies.catalog import KeywordsVocabulary


@implementer(IVocabularyFactory)
class CreatorsVocabulary(KeywordsVocabulary):
    keyword_index = "Creator"


CreatorsVocabularyFactory = CreatorsVocabulary()
