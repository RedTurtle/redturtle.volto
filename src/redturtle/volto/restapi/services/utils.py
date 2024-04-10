from redturtle.volto.interfaces import IRedTurtleVoltoAdditionalSiteSchema

try:
    from plone.base.interfaces.controlpanel import ISiteSchema
except ImportError:
    from Products.CMFPlone.interfaces.controlpanel import ISiteSchema

FIELD_MAPPING = {
    "site_logo": ISiteSchema,
    "site_logo_footer": IRedTurtleVoltoAdditionalSiteSchema,
    "site_favicon": ISiteSchema,
}
