from plone import api
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.i18n.interfaces import ILanguageSchema
from plone.registry.interfaces import IRegistry
from plone.restapi.testing import RelativeSession
from redturtle.volto.testing import REDTURTLE_VOLTO_API_FUNCTIONAL_TESTING
from transaction import commit
from zope.component import getUtility

import unittest


class TestNotFoundView(unittest.TestCase):
    layer = REDTURTLE_VOLTO_API_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.api_session = RelativeSession(self.portal_url, test=self)
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

    def test_html_request_to_unknown_url_returns_blank_404_page(self):
        response = self.api_session.get(
            "/this-page-does-not-exist", headers={"Accept": "text/html"}
        )

        self.assertEqual(response.status_code, 404)
        self.assertIn("text/html", response.headers.get("Content-Type", ""))
        self.assertIn("404", response.text)
        self.assertIn("Page not found", response.text)

    def test_html_request_with_italian_accept_language_is_translated(self):
        # Plone doesn't negotiate a language from the Accept-Language header
        # unless the site is explicitly configured to do so, and "it" has to
        # be listed as an available language to be picked.
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ILanguageSchema, prefix="plone")
        original_languages = settings.available_languages
        original_use_request_negotiation = settings.use_request_negotiation
        settings.available_languages = ["en", "it"]
        settings.use_request_negotiation = True
        commit()

        def _restore_settings():
            settings.available_languages = original_languages
            settings.use_request_negotiation = original_use_request_negotiation
            commit()

        self.addCleanup(_restore_settings)

        response = self.api_session.get(
            "/this-page-does-not-exist",
            headers={"Accept": "text/html", "Accept-Language": "it"},
        )

        self.assertEqual(response.status_code, 404)
        self.assertIn('lang="it"', response.text)
        self.assertIn("Pagina non trovata", response.text)
        self.assertIn("La pagina che stai cercando non esiste.", response.text)

    def test_non_html_request_to_unknown_url_returns_json_error(self):
        response = self.api_session.get(
            "/this-page-does-not-exist", headers={"Accept": "application/json"}
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.headers.get("Content-Type"), "application/json")
        self.assertEqual(response.json(), {"error_type": "NotFound"})

    def test_request_without_accept_header_returns_json_error(self):
        response = self.api_session.get(
            "/this-page-does-not-exist", headers={"Accept": ""}
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.headers.get("Content-Type"), "application/json")
        self.assertEqual(response.json(), {"error_type": "NotFound"})

    def test_moved_content_is_redirected_instead_of_returning_404(self):
        page = api.content.create(
            container=self.portal, type="Document", title="Old page"
        )
        old_id = page.getId()
        commit()

        new_id = "new-page-id"
        self.portal.manage_renameObject(id=old_id, new_id=new_id)
        commit()

        response = self.api_session.get(
            f"/{old_id}",
            headers={"Accept": "text/html"},
            allow_redirects=False,
        )

        self.assertIn(response.status_code, (301, 302, 307))
        self.assertIn(new_id, response.headers.get("Location", ""))
