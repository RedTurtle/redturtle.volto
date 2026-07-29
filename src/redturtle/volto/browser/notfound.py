from plone.memoize.view import memoize
from Products.Five import BrowserView
from zope.component import getMultiAdapter

import json


class NotFound(BrowserView):
    """Render a minimal, standalone 404 page.

    Overrides Plone's themed error page (which relies on frontend assets)
    for requests that hit this backend directly instead of Volto, e.g. an
    haproxy misconfiguration routing there instead of to the frontend.
    """

    @property
    @memoize
    def plone_redirector_view(self):
        return getMultiAdapter(
            (self.__parent__, self.request), name="plone_redirector_view"
        )

    def __call__(self):
        request = self.request

        if self.plone_redirector_view.attempt_redirect():
            # a redirect is possible: attempt_redirect already set the
            # Location header and status on the response.
            return ""

        request.response.setStatus(404)

        if "text/html" not in request.getHeader("Accept", ""):
            request.response.setHeader("Content-Type", "application/json")
            return json.dumps({"error_type": "NotFound"})

        return self.index()
