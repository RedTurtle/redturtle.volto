# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from redturtle.volto.interfaces import IRedTurtleVoltoSettings
from redturtle.volto.testing import REDTURTLE_VOLTO_INTEGRATION_TESTING
from zExceptions import BadRequest
from zope.container.interfaces import INameChooser

import unittest


class FakeObject:
    """"""

    def __of__(self, xxx):
        pass


class TestNameChooserDisabled(unittest.TestCase):
    """ """

    layer = REDTURTLE_VOLTO_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        foo = api.content.create(
            container=self.portal,
            type="Document",
            title="Foo",
        )

        self.bar = api.content.create(
            container=self.portal,
            type="Document",
            title="Bar",
        )

        api.content.rename(obj=foo, new_id="xxx")

    def test_by_default_customization_is_disabled_on_site_root(self):
        """Test that we cannot choose an already created alias"""
        fake_obj = FakeObject()
        chooser = INameChooser(self.portal)

        # can set an unused id
        self.assertEqual("unused-id", chooser.chooseName("unused id", fake_obj))

        # default behavior when trying to use an already-created id
        self.assertEqual("bar-1", chooser.chooseName("bar", fake_obj))

        # do not raise exception if the name is an alias
        self.assertEqual("foo", chooser.chooseName("foo", fake_obj))

    def test_by_default_customization_is_disabled_on_site_folderish_container(self):
        """Test that we cannot choose an already created alias"""
        container = api.content.create(
            container=self.portal,
            type="Document",
            title="container",
        )

        child = api.content.create(
            container=container,
            type="Document",
            title="aaa",
        )
        api.content.create(
            container=container,
            type="Document",
            title="bbb",
        )

        api.content.rename(obj=child, new_id="xxx")

        fake_obj = FakeObject()
        chooser = INameChooser(container)

        # can set an unused id
        self.assertEqual("unused-id", chooser.chooseName("unused id", fake_obj))

        # default behavior when trying to use an already-created id
        self.assertEqual("bbb-1", chooser.chooseName("bbb", fake_obj))

        # do not raise exception if the name is an alias
        self.assertEqual("aaa", chooser.chooseName("aaa", fake_obj))


class TestNameChooserEnabled(unittest.TestCase):
    """ """

    layer = REDTURTLE_VOLTO_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        foo = api.content.create(
            container=self.portal,
            type="Document",
            title="Foo",
        )

        self.bar = api.content.create(
            container=self.portal,
            type="Document",
            title="Bar",
        )

        api.content.rename(obj=foo, new_id="xxx")

        # enable it
        api.portal.set_registry_record(
            "check_aliases_in_namechooser", True, interface=IRedTurtleVoltoSettings
        )

    def test_name_chooser_raise_badrequest_on_site_root(self):
        """Test that we cannot choose an already created alias"""
        fake_obj = FakeObject()
        chooser = INameChooser(self.portal)

        # can set an unused id
        self.assertEqual("unused-id", chooser.chooseName("unused id", fake_obj))

        # default behavior when trying to use an already-created id
        self.assertEqual("bar-1", chooser.chooseName("bar", fake_obj))

        # raise exception if the name is an alias
        with self.assertRaises(BadRequest) as cm:
            chooser.chooseName("foo", fake_obj)

        self.assertEqual(
            'The id "foo" is invalid because there is already an alias for that path. Change its id or ask site administrators to remove "/foo" in aliases management.',
            str(cm.exception),
        )

    def test_if_enabled_name_chooser_raise_badrequest_on_folderish_container(self):
        """Test that we cannot choose an already created alias"""

        container = api.content.create(
            container=self.portal,
            type="Document",
            title="container",
        )

        child = api.content.create(
            container=container,
            type="Document",
            title="aaa",
        )
        api.content.create(
            container=container,
            type="Document",
            title="bbb",
        )

        api.content.rename(obj=child, new_id="xxx")

        fake_obj = FakeObject()
        chooser = INameChooser(container)

        # can set an unused id
        self.assertEqual("unused-id", chooser.chooseName("unused id", fake_obj))

        # can set an alias is used in another path
        self.assertEqual("foo", chooser.chooseName("foo", fake_obj))

        # default behavior when trying to use an already-created id in this context
        self.assertEqual("bbb-1", chooser.chooseName("bbb", fake_obj))

        # raise exception if the name is an alias
        with self.assertRaises(BadRequest) as cm:
            chooser.chooseName("aaa", fake_obj)

        self.assertEqual(
            'The id "aaa" is invalid because there is already an alias for that path. Change its id or ask site administrators to remove "/container/aaa" in aliases management.',
            str(cm.exception),
        )

    def test_api_rename_raise_exception_if_name_is_alias(self):
        """Test that we cannot choose an already created alias"""

        item = api.content.create(
            container=self.portal,
            type="Document",
            title="item",
        )
        with self.assertRaises(BadRequest) as cm:
            api.content.rename(obj=item, new_id="foo", safe_id=True)

        self.assertEqual(
            'The id "foo" is invalid because there is already an alias for that path. Change its id or ask site administrators to remove "/foo" in aliases management.',
            str(cm.exception),
        )

        # without safe_id=True, InameChooser will not be called
        res = api.content.rename(obj=item, new_id="foo")
        self.assertEqual(res.getId(), "foo")
