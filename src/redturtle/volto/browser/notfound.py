from plone.rest.errors import ErrorHandling
from plone.rest.interfaces import IAPIRequest
from Products.CMFPlone.browser.exceptions import ExceptionView


class NotFound(ExceptionView):
    """Render a minimal, standalone 404 page.

    Overrides Plone's themed error page (which relies on frontend assets)
    for requests that hit this backend directly instead of Volto, e.g. an
    haproxy misconfiguration routing there instead of to the frontend.

    Redirects (aliases, moved content) are still handled by Plone's
    standard logic, before rendering the template.

    This view is more specific than the default ones, so it also receives the
    API requests that plone.rest would normally handle. Those are given back
    to plone.rest: its redirect logic is the only one that knows about the
    "++api++" traverser used by Volto (plone.app.redirector's one never matches
    the stored aliases) and about named services.
    """

    def __call__(self):
        if IAPIRequest.providedBy(self.request):
            view = ErrorHandling(self.context, self.request)
            view.__parent__ = self.__parent__
            return view()

        # Never let the site theme wrap this page: it must stay
        # renderable even when the frontend/theme assets are unreachable,
        # which is the whole point of this view.
        self.request.response.setHeader("X-Theme-Disabled", "1")
        return super().__call__()
