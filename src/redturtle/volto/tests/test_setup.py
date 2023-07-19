# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from redturtle.volto.testing import REDTURTLE_VOLTO_INTEGRATION_TESTING  # noqa: E501

import unittest


try:
    from Products.CMFPlone.utils import get_installer
except ImportError:
    get_installer = None


class TestSetup(unittest.TestCase):
    """Test that redturtle.volto is properly installed."""

    layer = REDTURTLE_VOLTO_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        if get_installer:
            self.installer = get_installer(self.portal, self.layer["request"])
        else:
            self.installer = api.portal.get_tool("portal_quickinstaller")

    def test_product_installed(self):
        """Test if redturtle.volto is installed."""
        if hasattr(self.installer, "is_product_installed"):
            self.assertTrue(self.installer.is_product_installed("redturtle.volto"))
        else:
            self.assertTrue(self.installer.isProductInstalled("redturtle.volto"))

    def test_browserlayer(self):
        """Test that IRedturtleVoltoLayer is registered."""
        from plone.browserlayer import utils
        from redturtle.volto.interfaces import IRedturtleVoltoLayer

        self.assertIn(IRedturtleVoltoLayer, utils.registered_layers())

    def test_customized_restapi_permission(self):
        roles = self.portal.rolesOfPermission(
            "plone.restapi: Access Plone vocabularies"
        )
        enabled_roles = [x["name"] for x in roles if x["selected"] == "SELECTED"]
        self.assertEqual(
            enabled_roles,
            ["Anonymous", "Contributor", "Editor", "Manager", "Site Administrator"],
        )


class TestUninstall(unittest.TestCase):
    layer = REDTURTLE_VOLTO_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        if get_installer:
            self.installer = get_installer(self.portal, self.layer["request"])
        else:
            self.installer = api.portal.get_tool("portal_quickinstaller")
        roles_before = api.user.get_roles(TEST_USER_ID)
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        if hasattr(self.installer, "uninstall_product"):
            self.installer.uninstall_product("redturtle.volto")
        else:
            self.installer.uninstallProducts(["redturtle.volto"])
        setRoles(self.portal, TEST_USER_ID, roles_before)

    def test_product_uninstalled(self):
        """Test if redturtle.volto is cleanly uninstalled."""
        if hasattr(self.installer, "is_product_installed"):
            self.assertFalse(self.installer.is_product_installed("redturtle.volto"))
        else:
            self.assertFalse(self.installer.isProductInstalled("redturtle.volto"))

    def test_browserlayer_removed(self):
        """Test that IRedturtleVoltoLayer is removed."""
        from plone.browserlayer import utils
        from redturtle.volto.interfaces import IRedturtleVoltoLayer

        self.assertNotIn(IRedturtleVoltoLayer, utils.registered_layers())
