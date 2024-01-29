from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.dexterity.utils import iterSchemata
from plone.restapi.interfaces import IFieldDeserializer
from Products.CMFCore.utils import getToolByName
from redturtle.volto.testing import REDTURTLE_VOLTO_API_FUNCTIONAL_TESTING
from zope.component import getMultiAdapter

import transaction
import unittest


class TestDXFieldDeserializer(unittest.TestCase):
    layer = REDTURTLE_VOLTO_API_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.request = self.layer["request"]
        self.portal = self.layer["portal"]

        self.wftool = getToolByName(self.portal, "portal_workflow")
        self.acl_users = getToolByName(self.portal, "acl_users")

        self.acl_users.userFolderAddUser("user1", "secret", ["Manager"], [])
        self.acl_users.getUser("user1")

        login(self.portal, "user1")

        # folders
        self.portal.invokeFactory("Folder", id="folder", title="Private Folder")
        self.portal.folder.invokeFactory(
            "Folder", id="otherfolder", title="Other Folder"
        )
        self.wftool.doActionFor(self.portal.folder.otherfolder, "publish")

        self.portal.invokeFactory("Document", id="doc1", title="Test Document")
        self.wftool.doActionFor(self.portal.doc1, "publish")

        transaction.commit()

    def deserialize(self, fieldname, value):
        for schema in iterSchemata(self.portal.doc1):
            if fieldname in schema:
                field = schema.get(fieldname)
                break
        deserializer = getMultiAdapter(
            (field, self.portal.doc1, self.request), IFieldDeserializer
        )
        return deserializer(value)

    def test_relationlist_deserialization_broke_with_path(self):
        # documents
        doc2 = self.portal.folder.otherfolder[
            self.portal.folder.otherfolder.invokeFactory(
                "Document", id="doc2", title="Referenceable Document"
            )
        ]
        self.wftool.doActionFor(self.portal.folder.otherfolder.doc2, "publish")
        doc3 = self.portal.folder.otherfolder[
            self.portal.folder.otherfolder.invokeFactory(
                "Document", id="doc3", title="Referenceable Document"
            )
        ]
        self.wftool.doActionFor(self.portal.folder.otherfolder.doc3, "publish")

        setRoles(self.portal, TEST_USER_ID, ["Member"])
        login(self.portal, TEST_USER_NAME)

        try:
            value = self.deserialize(
                "relatedItems",
                [str(doc2.absolute_url_path()), str(doc3.absolute_url_path())],
            )
        except ValueError:
            value = None

        self.assertIsNone(value)

    def test_relationlist_deserialization_correct_with_uid(self):
        # documents
        doc2 = self.portal.folder.otherfolder[
            self.portal.folder.otherfolder.invokeFactory(
                "Document", id="doc2", title="Referenceable Document"
            )
        ]
        self.wftool.doActionFor(self.portal.folder.otherfolder.doc2, "publish")
        doc3 = self.portal.folder.otherfolder[
            self.portal.folder.otherfolder.invokeFactory(
                "Document", id="doc3", title="Referenceable Document"
            )
        ]
        self.wftool.doActionFor(self.portal.folder.otherfolder.doc3, "publish")

        setRoles(self.portal, TEST_USER_ID, ["Member"])
        login(self.portal, TEST_USER_NAME)

        value = self.deserialize(
            "relatedItems",
            [str(doc2.UID()), str(doc3.UID())],
        )

        self.assertTrue(value)
