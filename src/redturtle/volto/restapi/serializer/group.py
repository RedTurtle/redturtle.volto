from plone.restapi.batching import HypermediaBatch
from plone.restapi.interfaces import ISerializeToJson
from Products.PlonePAS.interfaces.group import IGroupData
from zope.component import adapter
from zope.interface import implementer
from redturtle.volto.interfaces import IRedturtleVoltoLayer
from Products.PluggableAuthService.interfaces.plugins import IRolesPlugin
from plone.restapi.serializer.group import BaseSerializer
from plone import api


@implementer(ISerializeToJson)
@adapter(IGroupData, IRedturtleVoltoLayer)
class SerializeGroupToJson(BaseSerializer):
    def __call__(self):
        data = super().__call__()
        group = self.context
        if group.id == 'AuthenticatedUsers':
            data['roles'] = []
            acl = api.portal.get_tool('acl_users')
            rolemakers = acl.plugins.listPlugins(IRolesPlugin)
            for rolemaker_id, rolemaker in rolemakers:
                roles = rolemaker.getRolesForPrincipal(group) or ()
                data['roles'].extend(roles)
            
        members = group.getGroupMemberIds()
        batch = HypermediaBatch(self.request, members)
        members_data = {
            "@id": batch.canonical_url,
            "items_total": batch.items_total,
            "items": sorted(batch),
        }
        if batch.links:
            members_data["batching"] = batch.links

        data["members"] = members_data
        return data


