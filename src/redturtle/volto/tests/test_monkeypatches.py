from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from Products.CMFPlone.interfaces import ISelectableConstrainTypes
from redturtle.volto.testing import REDTURTLE_VOLTO_FUNCTIONAL_TESTING
from unittest import mock

import unittest


class TestRespectLocallyAllowedTypes(unittest.TestCase):
    layer = REDTURTLE_VOLTO_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.folder = api.content.create(
            container=self.portal,
            type="Folder",
            title="Folder",
            description="",
        )
        self.document = api.content.create(
            container=self.portal,
            type="Document",
            title="Page",
            description="",
        )
        self.news = api.content.create(
            container=self.portal,
            type="News Item",
            title="News",
            description="",
        )

    def test_cant_paste_with_filter_set(self):
        self.folder._verifyObjectPaste(self.document)

        constraints = ISelectableConstrainTypes(self.folder)
        constraints.setConstrainTypesMode(1)
        constraints.setLocallyAllowedTypes(("News Item",))

        self.assertRaises(ValueError, self.folder._verifyObjectPaste, self.document)
        self.folder._verifyObjectPaste(self.news)


class TestMailHostSendLogging(unittest.TestCase):
    layer = REDTURTLE_VOLTO_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.mailhost = self.portal.MailHost

    def test_send_is_patched_with_old_send_preserved(self):
        self.assertTrue(hasattr(self.mailhost, "_old_send"))

    def test_send_logs_and_calls_original_send(self):
        with mock.patch.object(self.mailhost, "_old_send") as old_send:
            with self.assertLogs("redturtle.volto.monkey", level="INFO") as cm:
                self.mailhost.send(
                    "message body",
                    mto="to@example.com",
                    mfrom="from@example.com",
                    subject="a subject",
                )

        old_send.assert_called_once_with(
            "message body",
            mto="to@example.com",
            mfrom="from@example.com",
            subject="a subject",
        )
        self.assertIn("to@example.com", cm.output[0])
        self.assertIn("from@example.com", cm.output[0])
        self.assertIn("a subject", cm.output[0])
