from Products.CMFPlone.browser.exceptions import ExceptionView


class RTExceptionView(ExceptionView):

    def __call__(self):
        matches = ["@@download", "@@images", "@@display-file"]

        if any(x in self.request.environ.get("REQUEST_URI") for x in matches):
            return self.request.response.redirect(self.request.URL)

        return super(RTExceptionView, self).__call__()
