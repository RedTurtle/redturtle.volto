from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from Products.CMFCore.CMFCatalogAware import CatalogAware
from redturtle.volto.testing import REDTURTLE_VOLTO_INTEGRATION_TESTING
from unittest import mock

import unittest


class TestDeleteLocalRoles(unittest.TestCase):
    layer = REDTURTLE_VOLTO_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.mtool = api.portal.get_tool("portal_membership")
        self.catalog = api.portal.get_tool("portal_catalog")
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        api.user.create(email="mario@example.com", username="mario")
        api.user.create(email="luigi@example.com", username="luigi")
        api.group.create(groupname="redattori")

        # /folder (redattori: Editor)
        #   /subfolder (redattori: Editor, mario: Reader)
        #     /document (mario: Editor)
        # /other
        #   /other-document
        self.folder = api.content.create(
            container=self.portal, type="Folder", title="Folder"
        )
        self.subfolder = api.content.create(
            container=self.folder, type="Folder", title="Subfolder"
        )
        self.document = api.content.create(
            container=self.subfolder, type="Document", title="Document"
        )
        self.other = api.content.create(
            container=self.portal, type="Folder", title="Other"
        )
        self.other_document = api.content.create(
            container=self.other, type="Document", title="Other document"
        )
        # "redattori" comes before "mario" in the local roles: the first
        # version of the patch stopped scanning at the first interesting role
        # and never deleted mario's one.
        self.folder.manage_setLocalRoles("redattori", ["Editor"])
        self.subfolder.manage_setLocalRoles("redattori", ["Editor"])
        self.subfolder.manage_setLocalRoles("mario", ["Reader"])
        self.document.manage_setLocalRoles("mario", ["Editor"])
        for obj in (self.folder, self.subfolder, self.document):
            obj.reindexObjectSecurity()

    def local_users(self, obj):
        return [user for user, roles in obj.get_local_roles()]

    def paths_with_allowed(self, principal):
        return sorted(
            brain.getPath()
            for brain in self.catalog.unrestrictedSearchResults(
                allowedRolesAndUsers=principal
            )
        )

    def path(self, obj):
        return "/".join(obj.getPhysicalPath())

    def test_delete_members_removes_local_roles(self):
        self.mtool.deleteMembers(["mario"])

        self.assertNotIn("mario", self.local_users(self.subfolder))
        self.assertNotIn("mario", self.local_users(self.document))
        self.assertIn("redattori", self.local_users(self.subfolder))

    def test_delete_local_roles_removes_role_after_other_interesting_roles(self):
        self.mtool.deleteLocalRoles(self.portal, ["mario"], reindex=1, recursive=1)

        self.assertNotIn("mario", self.local_users(self.subfolder))
        self.assertIn("redattori", self.local_users(self.subfolder))

    def test_security_indexes_are_updated(self):
        self.assertEqual(
            self.paths_with_allowed("user:mario"),
            [self.path(self.subfolder), self.path(self.document)],
        )

        self.mtool.deleteLocalRoles(self.portal, ["mario"], reindex=1, recursive=1)

        self.assertEqual(self.paths_with_allowed("user:mario"), [])
        # other principals are untouched
        self.assertIn(
            self.path(self.document), self.paths_with_allowed("user:redattori")
        )

    def test_reindex_only_topmost_modified_objects(self):
        with mock.patch.object(
            CatalogAware, "reindexObjectSecurity", autospec=True
        ) as reindex:
            self.mtool.deleteLocalRoles(self.portal, ["mario"], reindex=1, recursive=1)

        # document is inside subfolder: reindexObjectSecurity is recursive,
        # so only subfolder is reindexed. The portal is never reindexed.
        self.assertEqual(
            [self.path(call.args[0]) for call in reindex.call_args_list],
            [self.path(self.subfolder)],
        )

    def test_no_reindex_if_nothing_deleted(self):
        with mock.patch.object(
            CatalogAware, "reindexObjectSecurity", autospec=True
        ) as reindex:
            self.mtool.deleteLocalRoles(self.portal, ["luigi"], reindex=1, recursive=1)

        reindex.assert_not_called()

    def test_no_reindex_if_reindex_false(self):
        with mock.patch.object(
            CatalogAware, "reindexObjectSecurity", autospec=True
        ) as reindex:
            self.mtool.deleteLocalRoles(self.portal, ["mario"], reindex=0, recursive=1)

        reindex.assert_not_called()
        self.assertNotIn("mario", self.local_users(self.document))

    def test_not_recursive(self):
        self.mtool.deleteLocalRoles(self.subfolder, ["mario"], reindex=1)

        self.assertNotIn("mario", self.local_users(self.subfolder))
        self.assertIn("mario", self.local_users(self.document))

    def test_depth_skips_uninteresting_subtrees(self):
        # like real sites, the portal has some group roles, otherwise with
        # depth=1 the search stops at the portal itself
        self.portal.manage_setLocalRoles("redattori", ["Reader"])
        # other has only the Owner role: with depth=1 its subtree is skipped
        self.other_document.manage_setLocalRoles("mario", ["Editor"])

        self.mtool.deleteLocalRoles(
            self.portal, ["mario"], reindex=1, recursive=1, depth=1
        )

        self.assertIn("mario", self.local_users(self.other_document))
        # folder has interesting roles, so its subtree is still visited
        self.assertNotIn("mario", self.local_users(self.document))

    def test_default_depth_reaches_nested_roles(self):
        self.other_document.manage_setLocalRoles("mario", ["Editor"])

        self.mtool.deleteLocalRoles(self.portal, ["mario"], reindex=1, recursive=1)

        self.assertNotIn("mario", self.local_users(self.other_document))
