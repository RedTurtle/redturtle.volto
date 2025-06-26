from ddtrace.contrib.wsgi import DDWSGIMiddleware
import ddtrace
# ??? serve questo ???
ddtrace.patch(logging=True)


def make_dd_middleware(app, *args, **kwargs):
    return DDWSGIMiddleware(app)
