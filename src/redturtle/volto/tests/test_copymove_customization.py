# -*- coding: utf-8 -*-
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.restapi.testing import RelativeSession
from redturtle.volto.interfaces import IRedTurtleVoltoSettings
from redturtle.volto.testing import REDTURTLE_VOLTO_API_FUNCTIONAL_TESTING

import transaction
import unittest


class TestCopyMoveCustomization(unittest.TestCase):
    layer = REDTURTLE_VOLTO_API_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

        foo = api.content.create(
            container=self.portal,
            type="Document",
            title="Foo",
        )
        api.content.rename(obj=foo, new_id="xxx")

        self.bar = api.content.create(
            container=self.portal,
            type="Document",
            title="Bar",
        )
        api.content.create(
            container=self.bar,
            type="Document",
            title="foo",
        )

        # enable it
        api.portal.set_registry_record(
            "check_aliases_in_namechooser", True, interface=IRedTurtleVoltoSettings
        )

        transaction.commit()

    def tearDown(self):
        self.api_session.close()

    def test_move_raise_error_if_id_is_a_valid_alias(self):
        response = self.api_session.post("/@move", json={"source": ["/bar/foo"]})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["message"],
            'The id "foo" is invalid because there is already an alias for that path. Change its id or ask site administrators to remove "/foo" in aliases management.',
        )

    def test_copy_raise_error_if_id_is_a_valid_alias(self):
        response = self.api_session.post("/@copy", json={"source": ["/bar/foo"]})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["message"],
            'The id "foo" is invalid because there is already an alias for that path. Change its id or ask site administrators to remove "/foo" in aliases management.',
        )
