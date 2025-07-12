from ddtrace.contrib.wsgi import DDWSGIMiddleware
import ddtrace
# ??? serve questo ???
ddtrace.patch(logging=True)


class FilteredDDWSGIMiddleware(DDWSGIMiddleware):

    def __call__(self, environ, start_response):
        if environ.get("PATH_INFO") and environ.get("PATH_INFO").endswith("/@@ok"):
            return self.app(environ, start_response)
        return super().__call__(environ, start_response)


def make_dd_middleware(app, *args, **kwargs):
    return FilteredDDWSGIMiddleware(app)


#def make_dd_middleware(app, *args, **kwargs):
#    return DDWSGIMiddleware(app)
