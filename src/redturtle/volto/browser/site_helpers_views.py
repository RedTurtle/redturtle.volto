from plone.formwidget.namedfile.converter import b64decode_file
from plone.namedfile.browser import Download
from plone.namedfile.file import NamedImage
from plone.registry.interfaces import IRegistry
from zope.component import getUtility


try:
    from plone.base.interfaces.controlpanel import ISiteSchema
except ImportError:
    from Products.CMFPlone.interfaces.controlpanel import ISiteSchema


class BaseView(Download):
    def __init__(self, context, request):
        super().__init__(context, request)
        self.filename = None
        self.data = None

        registry = getUtility(IRegistry)
        settings = registry.forInterface(ISiteSchema, prefix="plone")
        value = getattr(settings, self.field_name, False)
        if value:
            filename, data = b64decode_file(value)
            data = NamedImage(data=data, filename=filename)
            self.data = data
            self.filename = filename
            # self.width, self.height = self.data.getImageSize()

    def _getFile(self):
        return self.data


class Favicon(BaseView):
    field_name = "site_favicon"


class LogoFooter(BaseView):
    field_name = "site_logo_footer"
