from plone.rest.errors import ErrorHandling
from Products.Five import BrowserView

import json


class NotFound(BrowserView):
    """Render a minimal, standalone 404 page.

    Overrides Plone's themed error page (which relies on frontend assets)
    for requests that hit this backend directly instead of Volto, e.g. an
    haproxy misconfiguration routing there instead of to the frontend.
    """

    def attempt_redirect(self):
        # Use plone.rest's redirect logic instead of plone.app.redirector's
        # one: Volto reaches the backend through the "++api++" traverser,
        # which plone.app.redirector doesn't strip, so it never matches the
        # stored aliases. This view is more specific than plone.rest's
        # error view, so it would otherwise shadow it.
        return ErrorHandling(self.context, self.request).attempt_redirect()

    def __call__(self):
        request = self.request

        if self.attempt_redirect():
            # a redirect is possible: attempt_redirect already set the
            # Location header and status on the response.
            return ""

        request.response.setStatus(404)
        # Never let the site theme wrap this page: it must stay
        # renderable even when the frontend/theme assets are unreachable,
        # which is the whole point of this view.
        request.response.setHeader("X-Theme-Disabled", "1")

        if "text/html" not in request.getHeader("Accept", ""):
            request.response.setHeader("Content-Type", "application/json")
            return json.dumps({"error_type": "NotFound"})

        return self.index()
