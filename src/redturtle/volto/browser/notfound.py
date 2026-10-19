from plone.rest.errors import ErrorHandling

import json


class NotFound(ErrorHandling):
    """Render a minimal, standalone 404 page.
    Overrides Plone's themed error page (which relies on frontend assets)
    for requests that hit this backend directly instead of Volto.
    """

    def __call__(self):
        request = self.request

        if self.attempt_redirect():
            # a redirect is possible: attempt_redirect already set the
            # Location header and status on the response.
            return ""

        request.response.setStatus(404)
        # Never let the site theme wrap this page.
        request.response.setHeader("X-Theme-Disabled", "1")

        if "text/html" not in request.getHeader("Accept", ""):
            request.response.setHeader("Content-Type", "application/json")
            return json.dumps({"error_type": "NotFound"})

        return self.index()
