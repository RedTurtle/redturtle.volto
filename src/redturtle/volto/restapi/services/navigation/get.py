# -*- coding: utf-8 -*-
from plone.app.layout.navigation.navtree import buildFolderTree
from plone.app.layout.navigation.navtree import NavtreeStrategyBase
from plone.dexterity.interfaces import IDexterityContainer
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.services import Service
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface


@implementer(IExpandableElement)
@adapter(IDexterityContainer, Interface)
class ContextNavigation(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, expand=False):
        if self.request.form.get("expand.navigation.depth", False):
            depth = int(self.request.form["expand.navigation.depth"])
        else:
            depth = 1
        result = {
            "navigation": {
                "@id": "{}/@context-navigation".format(
                    self.context.absolute_url()
                )
            }
        }
        if not expand:
            return result

        root = self.context

        class Strategy(NavtreeStrategyBase):

            rootPath = '/'.join(root.getPhysicalPath())
            showAllParents = False

        strategy = Strategy()
        query = {
            'path': {
                'query': '/'.join(root.getPhysicalPath()),
                'depth': depth,
            },
            'is_folderish': True,
            'sort_on': 'getObjPositionInParent',
        }

        navtree = buildFolderTree(self, query=query, strategy=strategy)
        items = {
            '@id': self.context.absolute_url(),
            'items': [self.generateNode(x) for x in navtree['children']],
        }
        return items

    def generateNode(self, root):
        item = root['item']
        res = {
            "title": item.Title,
            "@id": item.getURL(),
            "description": item.Description,
        }
        children = root.get('children', [])
        if children:
            res["items"] = [self.generateNode(x) for x in children]
        return res


class NavigationGet(Service):
    def reply(self):
        navigation = ContextNavigation(self.context, self.request)
        return navigation(expand=True)
