# -*- coding: utf-8 -*-
from Products.CMFPlone.interfaces import INonInstallable
from zope.interface import implementer
from redturtle.volto.upgrades import upgrade_robots_txt


@implementer(INonInstallable)
class HiddenProfiles(object):
    def getNonInstallableProfiles(self):
        """Hide uninstall profile from site-creation and quickinstaller."""
        return ["redturtle.volto:uninstall"]


def post_install(context):
    """Post install script"""
    upgrade_robots_txt(context)


def uninstall(context):
    """Uninstall script"""
    # Do something at the end of the uninstallation of this package.
