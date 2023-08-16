import os


def manage_auth_token(event):
    """
    set authorization header from cookie

    see:
        https://github.com/plone/plone.restapi/issues/148
        https://github.com/plone/plone.restapi/pull/1303
    """
    if os.environ.get("PROXY_BEARER_AUTH"):
        request = event.request
        if getattr(request, "_auth", None):
            return
        auth_token = request.cookies.get("auth_token")
        if auth_token:
            request._auth = "Bearer " + auth_token
