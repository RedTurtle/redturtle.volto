from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from Products.CMFPlone.interfaces import ISelectableConstrainTypes
from redturtle.volto.monkey import _get_smtp_timeout
from redturtle.volto.testing import REDTURTLE_VOLTO_FUNCTIONAL_TESTING
from unittest import mock
from zope.sendmail.mailer import SMTPMailer

import os
import redturtle.volto.monkey
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


class TestSMTPMailerTimeout(unittest.TestCase):
    layer = REDTURTLE_VOLTO_FUNCTIONAL_TESTING

    def test_init_is_patched_with_old_init_preserved(self):
        self.assertTrue(hasattr(SMTPMailer, "_old___init__"))

    def test_vote_is_patched_with_old_vote_preserved(self):
        self.assertTrue(hasattr(SMTPMailer, "_old_vote"))

    def test_default_timeout_is_10_seconds(self):
        mailer = SMTPMailer()
        self.assertEqual(mailer.timeout, 10)

    def test_timeout_is_used_in_vote(self):
        mailer = SMTPMailer()
        with mock.patch.object(mailer, "smtp") as smtp:
            smtp.return_value.ehlo.return_value = (250, "ok")
            mailer.vote("from@example.com", ["to@example.com"], "message")

        smtp.assert_called_once_with("localhost", "25", timeout=10)

    def test_timeout_parsed_from_environment(self):
        with mock.patch.dict(os.environ, {"REDTURTLE_VOLTO_SMTP_TIMEOUT": "5"}):
            self.assertEqual(_get_smtp_timeout(), 5.0)

    def test_timeout_can_be_disabled_via_environment(self):
        with mock.patch.dict(os.environ, {"REDTURTLE_VOLTO_SMTP_TIMEOUT": "None"}):
            self.assertIsNone(_get_smtp_timeout())

    def test_timeout_configurable_via_environment_is_used_by_init(self):
        with mock.patch.object(redturtle.volto.monkey, "SMTP_TIMEOUT", 5):
            mailer = SMTPMailer()
        self.assertEqual(mailer.timeout, 5)

    def test_disabled_timeout_is_not_passed_to_smtp(self):
        with mock.patch.object(redturtle.volto.monkey, "SMTP_TIMEOUT", None):
            mailer = SMTPMailer()
        with mock.patch.object(mailer, "smtp") as smtp:
            smtp.return_value.ehlo.return_value = (250, "ok")
            mailer.vote("from@example.com", ["to@example.com"], "message")
        smtp.assert_called_once_with("localhost", "25")
