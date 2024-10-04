from plone import api
from plone.namedfile.browser import Download as BaseDownload
from plone.namedfile.utils import set_headers


class Download(BaseDownload):
    """
    Customization to allow downloading miniature images with their original
    filename and not with miniature as filename.
    """

    def set_headers(self, file):
        """
        in self.filename we have the miniature name
        """
        filename = getattr(file, "filename", None)
        if self.filename:
            # we are downloading a miniature
            filename = f"{self.filename}_{filename}"
        set_headers(file, self.request.response, filename=filename)

    def _getFile(self):
        """
        in self.filename we have the miniature name
        """
        if self.filename:
            # we are downloading a miniature
            view = api.content.get_view(
                name="images", context=self.context, request=self.request
            )
            scale = view.scale(scale=self.filename, fieldname=self.fieldname)
            if scale:
                return scale.data
        return super()._getFile()
