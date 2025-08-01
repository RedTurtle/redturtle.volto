from Products.CMFPlone.browser.exceptions import ExceptionView


class RTExceptionView(ExceptionView):

    def __call__(self):
        matches = ["@@download", "@@images", "@@display-file"]
        if any(x in self.request.ACTUAL_URL for x in matches):
            self.request.response.redirect(self.request.URL, status=302, lock=1)
            return

        return super().__call__()
