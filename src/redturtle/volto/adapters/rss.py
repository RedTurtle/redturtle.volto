from DateTime import DateTime
from plone import api
from plone.api.exc import InvalidParameterError
from plone.app.contenttypes.behaviors.leadimage import ILeadImageBehavior
from plone.app.contenttypes.interfaces import IEvent
from plone.dexterity.interfaces import IDexterityContent
from plone.namedfile.interfaces import INamedField
from plone.rfc822.interfaces import IPrimaryFieldInfo
from plone.volto.behaviors.preview import IPreview
from redturtle.volto.interfaces import ICustomFeedItem


try:
    from plone.base.interfaces.syndication import IFeed
except ModuleNotFoundError:
    from Products.CMFPlone.interfaces.syndication import IFeed

from Products.CMFPlone.browser.syndication.adapters import DexterityItem
from zope.component import adapter


@adapter(ICustomFeedItem, IFeed)
class CustomFeedItem(DexterityItem):
    def _has_valid_image(self, behavior, field_name):
        if not behavior:
            return False

        field = getattr(behavior, field_name, None)
        if not field:
            return False

        if not hasattr(field, "getSize"):
            return False

        return field.getSize() > 0

    def __init__(self, context, feed):
        super().__init__(context, feed)
        self.dexterity = IDexterityContent.providedBy(context)
        self.img_choice = None
        self.file = None
        self.field_name = None
        self._set_image_field()
        if self.file is None:
            self._set_primary_field()

    def _set_image_field(self):
        lead = ILeadImageBehavior(self.context, None)
        preview = IPreview(self.context, None)
        # if we don't have the record gently fallback on the old behavior
        try:
            img_choice = api.portal.get_registry_record(
                "redturtle.volto.rss_image_choice"
            )
        except InvalidParameterError:
            # seems the default of get_registry_record is not working
            img_choice = "image"

        if img_choice == "preview_image" and self._has_valid_image(
            preview, "preview_image"
        ):
            self.file = preview.image
            self.field_name = "preview_image"
        elif img_choice == "image" and self._has_valid_image(lead, "image"):
            self.file = lead.image
            self.field_name = "image"
        elif img_choice == "listing_like":
            if self._has_valid_image(preview, "preview_image"):
                self.file = preview.image
                self.field_name = "preview_image"
            elif self._has_valid_image(lead, "image"):
                self.file = lead.image
                self.field_name = "image"

    def _set_primary_field(self):
        try:
            primary = IPrimaryFieldInfo(self.context, None)
            if (
                INamedField.providedBy(primary.field)
                and hasattr(primary.value, "getSize")  # noqa
                and primary.value.getSize() > 0  # noqa
            ):
                self.file = primary.value
                self.field_name = primary.fieldname
        except TypeError:
            pass


@adapter(IEvent, IFeed)
class EventItem(CustomFeedItem):
    @property
    def startdate(self):
        """
        Same format as other dates in
        Products.CMFPlone.browser.syndication.adapters
        """
        date = self.context.start.isoformat()
        if date:
            return DateTime(date)
