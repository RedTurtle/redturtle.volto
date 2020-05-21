# -*- coding: utf-8 -*-
import unittest

import transaction
from plone import api
from plone.app.testing import (
    SITE_OWNER_NAME,
    SITE_OWNER_PASSWORD,
    TEST_USER_ID,
    setRoles,
)
from plone.restapi.testing import RelativeSession
from redturtle.volto.testing import REDTURTLE_VOLTO_API_FUNCTIONAL_TESTING


class TestServicesContextNavigation(unittest.TestCase):

    layer = REDTURTLE_VOLTO_API_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

        folder = api.content.create(
            container=self.portal,
            type='Folder',
            title='Folder',
            description="",
        )
        api.content.create(
            container=folder, type='Document', title='Page', description=""
        )

        folder2 = api.content.create(
            container=folder, type='Folder', title='Folder A', description=""
        )

        api.content.create(
            container=folder, type='Folder', title='Folder B', description=""
        )

        api.content.create(
            container=folder, type='Folder', title='Folder C', description=""
        )

        api.content.create(
            container=folder2, type='Folder', title='Folder AA', description=""
        )

        api.content.create(
            container=folder2, type='Folder', title='Folder AB', description=""
        )

        transaction.commit()

    def tearDown(self):
        self.api_session.close()

    def test_context_navigation(self):
        response = self.api_session.get("/folder/@context-navigation")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                '@id': '{}/folder'.format(self.portal_url),
                'items': [
                    {
                        '@id': '{}/folder/page'.format(self.portal_url),
                        'description': '',
                        'title': 'Page',
                    },
                    {
                        '@id': '{}/folder/folder-a'.format(self.portal_url),
                        'description': '',
                        'title': 'Folder A',
                    },
                    {
                        '@id': '{}/folder/folder-b'.format(self.portal_url),
                        'description': '',
                        'title': 'Folder B',
                    },
                    {
                        '@id': '{}/folder/folder-c'.format(self.portal_url),
                        'description': '',
                        'title': 'Folder C',
                    },
                ],
            },
        )

    def test_context_navigation_depth_2(self):
        response = self.api_session.get(
            "/folder/@context-navigation?expand.navigation.depth=2"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                '@id': '{}/folder'.format(self.portal_url),
                'items': [
                    {
                        '@id': '{}/folder/page'.format(self.portal_url),
                        'description': '',
                        'title': 'Page',
                    },
                    {
                        '@id': '{}/folder/folder-a'.format(self.portal_url),
                        'description': '',
                        'items': [
                            {
                                '@id': '{}/folder/folder-a/folder-aa'.format(
                                    self.portal_url
                                ),
                                'description': '',
                                'title': 'Folder AA',
                            },
                            {
                                '@id': '{}/folder/folder-a/folder-ab'.format(
                                    self.portal_url
                                ),
                                'description': '',
                                'title': 'Folder AB',
                            },
                        ],
                        'title': 'Folder A',
                    },
                    {
                        '@id': '{}/folder/folder-b'.format(self.portal_url),
                        'description': '',
                        'title': 'Folder B',
                    },
                    {
                        '@id': '{}/folder/folder-c'.format(self.portal_url),
                        'description': '',
                        'title': 'Folder C',
                    },
                ],
            },
        )
