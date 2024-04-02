from plone.base.interfaces.controlpanel import ISiteSchema
from plone.formwidget.namedfile.converter import b64decode_file
from plone.namedfile.file import NamedImage
from plone.restapi.deserializer import json_body
from plone.restapi.deserializer.controlpanels import ControlpanelDeserializeFromJson
from plone.restapi.deserializer.controlpanels import FakeDXContext
from plone.restapi.interfaces import IDeserializeFromJson
from plone.restapi.interfaces import IFieldDeserializer
from redturtle.volto.interfaces import IRedTurtleVoltoAdditionalSiteSchema
from redturtle.volto.interfaces import IRedTurtleVoltoSiteControlpanel
from z3c.form.interfaces import IManagerValidator
from zExceptions import BadRequest
from zope.component import adapter
from zope.component import queryMultiAdapter
from zope.interface import implementer
from zope.schema import getFields
from zope.schema.interfaces import ValidationError


@implementer(IDeserializeFromJson)
@adapter(IRedTurtleVoltoSiteControlpanel)
class RedTurtleVoltoSiteSettingsDeserializeFromJson(ControlpanelDeserializeFromJson):
    def __call__(self):
        """
        Store data in the right registry records.
        We are keeping standard Plone fields in original registry interface to
        not comprimise other functionalities.
        """
        data = json_body(self.controlpanel.request)
        for schema_interface in [ISiteSchema, IRedTurtleVoltoAdditionalSiteSchema]:

            proxy = self.registry.forInterface(
                schema_interface, prefix=self.schema_prefix
            )

            schema_data = {}
            errors = []

            # Make a fake context
            fake_context = FakeDXContext()

            for name, field in getFields(self.schema).items():
                field_data = schema_data.setdefault(self.schema, {})

                if field.readonly:
                    continue

                if name in data:
                    deserializer = queryMultiAdapter(
                        (field, fake_context, self.request), IFieldDeserializer
                    )

                    try:
                        # Make it sane
                        value = deserializer(data[name])
                        # Validate required etc
                        field.validate(value)
                        # Set the value.
                        setattr(proxy, name, value)
                    except ValueError as e:
                        errors.append({"message": str(e), "field": name, "error": e})
                    except ValidationError as e:
                        errors.append({"message": e.doc(), "field": name, "error": e})
                    else:
                        field_data[name] = value

            # Validate schemata
            for schema, field_data in schema_data.items():
                validator = queryMultiAdapter(
                    (self.context, self.request, None, schema, None), IManagerValidator
                )
                for error in validator.validate(field_data):
                    errors.append({"error": error, "message": str(error)})

            if errors:
                raise BadRequest(errors)

        # set width and height for logo and favicon
        proxy = self.registry.forInterface(
            IRedTurtleVoltoAdditionalSiteSchema, prefix=self.schema_prefix
        )
        for field in ["logo", "logo_footer", "favicon"]:
            b64_data = data.get(f"site_{field}", "")
            if not b64_data:
                continue
            filename, img_data = b64decode_file(b64_data)
            image = NamedImage(data=img_data, filename=filename)
            width, height = image.getImageSize()
            if width and height:
                setattr(proxy, f"site_{field}_width", width)
                setattr(proxy, f"site_{field}_height", height)
