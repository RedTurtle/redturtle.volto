# -*- coding: utf-8 -*-
from plone import api
from Products.CMFPlone.interfaces import INonInstallable
from zope.interface import implementer

import logging


logger = logging.getLogger(__name__)


@implementer(INonInstallable)
class HiddenProfiles(object):
    def getNonInstallableProfiles(self):
        """Hide uninstall profile from site-creation and quickinstaller."""
        return ["redturtle.volto:uninstall"]


# DEPRECATED
def upgrade_robots_txt(context):
    robots = api.portal.get_registry_record("plone.robots_txt")
    lines = robots.splitlines()

    googlebot_user_agent = "User-Agent: Googlebot"
    # I saw this writed also as googlebot, so:
    normalized_google_bot_user_agent = googlebot_user_agent.lower().replace(" ", "")

    useragent_string = "User-Agent: "
    normalized_useragent_string = useragent_string.lower().replace(" ", "")

    googlebot_allow_rule = "Allow: /*?expand*"

    googlebot_index = -1
    allow_rule_present = False
    for i, line in enumerate(lines):
        if line.lower().replace(" ", "") == normalized_google_bot_user_agent:
            googlebot_index = i
        elif (
            googlebot_index != -1
            and line.replace(" ", "").lower()  # noqa
            == googlebot_allow_rule.replace(" ", "").lower()  # noqa
        ):
            allow_rule_present = True

    if googlebot_index != -1 and not allow_rule_present:
        # Trova l'indice della fine della sezione User-Agent: Googlebot
        end_googlebot_index = googlebot_index + 1
        while end_googlebot_index < len(lines) and not lines[
            end_googlebot_index
        ].lower().replace(" ", "").startswith(normalized_useragent_string):
            end_googlebot_index += 1

        # Aggiungi Allow: /*?expand* alla fine della sezione User-Agent: Googlebot
        if lines[end_googlebot_index - 1] == "":
            end_googlebot_index -= 1
        lines.insert(end_googlebot_index, googlebot_allow_rule)

        lines = "\n".join(lines)
        api.portal.set_registry_record("plone.robots_txt", lines)
        logger.info("Upgrade robots.txt with rule for googlebot")
    else:
        logger.info(
            "Rule for Googlebot already present in robots.txt, no action needed"
        )


def remove_custom_googlebot(context):
    robots = api.portal.get_registry_record("plone.robots_txt")
    googlebot_user_agent = "User-Agent: Googlebot".lower().replace(" ", "")
    lines = []
    googlebot = False
    for line in robots.splitlines():
        if line.lower().replace(" ", "") == googlebot_user_agent:
            googlebot = True
        elif line.startswith("User-Agent:"):
            googlebot = False
        if not googlebot:
            lines.append(line)
    lines = "\n".join(lines)
    api.portal.set_registry_record("plone.robots_txt", lines)
    logger.info("Upgrade robots.txt removing custom googlebot")


def post_install(context):
    """Post install script"""
    remove_custom_googlebot(context)


def uninstall(context):
    """Uninstall script"""
    # Do something at the end of the uninstallation of this package.
