from plone import api
from plone.restapi.services import Service
from plone.restapi.services.navigation.get import Navigation
from redturtle.volto.interfaces import IRedTurtleVoltoSettings


class SitemapSettingsGet(Service):
    def reply(self):
        return {"depth": api.portal.get_registry_record("plone.sitemap_depth")}


class SitemapNavigation(Navigation):
    """
    Same tree of @navigation, but without the content-types selected in the
    "sitemap_page_excluded_types" setting.
    """

    @property
    def excluded_types(self):
        try:
            return (
                api.portal.get_registry_record(
                    "sitemap_page_excluded_types",
                    interface=IRedTurtleVoltoSettings,
                )
                or []  # noqa
            )
        except KeyError:
            # record not registered yet (upgrade step 4800 not run)
            return []

    @property
    def settings(self):
        settings = dict(super().settings)
        excluded = self.excluded_types
        settings["displayed_types"] = tuple(
            x for x in settings["displayed_types"] if x not in excluded
        )
        return settings

    @property
    def portal_tabs(self):
        """
        First level contents are provided by portal_tabs and not by the catalog
        query that uses `settings`: filter them here.
        """
        tabs = super().portal_tabs
        excluded = self.excluded_types
        if not excluded:
            return tabs
        # tabs don't have the portal_type, so we need to ask it to the catalog.
        # (portal_tabs are already filtered by permissions)
        brains = api.content.find(
            path={"query": self.navtree_path, "depth": 1},
            portal_type=list(excluded),
        )
        excluded_ids = {brain.getId for brain in brains}
        return [tab for tab in tabs if tab["id"] not in excluded_ids]


class SitemapGet(Service):
    """
    Data for the sitemap page (the one visible to users).
    It has nothing to do with sitemap.xml.gz.

    `expand.navigation.depth` can be passed as in @navigation; by default the
    `plone.sitemap_depth` registry setting is used.
    """

    def reply(self):
        depth = api.portal.get_registry_record("plone.sitemap_depth")
        if "expand.navigation.depth" not in self.request.form:
            self.request.form["expand.navigation.depth"] = depth
        navigation = SitemapNavigation(self.context, self.request)
        items = navigation(expand=True)["navigation"]["items"]
        return {"depth": depth, "items": items}
