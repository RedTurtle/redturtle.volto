# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.restapi.testing import PloneRestApiDXLayer
from plone.testing import z2


import collective.folderishtypes
import collective.volto.cookieconsent
import plone.restapi
import redturtle.volto


class RedturtleVoltoLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        self.loadZCML(package=collective.folderishtypes)
        self.loadZCML(package=collective.volto.cookieconsent)
        self.loadZCML(package=plone.restapi)
        self.loadZCML(package=redturtle.volto)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'redturtle.volto:default')


REDTURTLE_VOLTO_FIXTURE = RedturtleVoltoLayer()


REDTURTLE_VOLTO_INTEGRATION_TESTING = IntegrationTesting(
    bases=(REDTURTLE_VOLTO_FIXTURE,),
    name='RedturtleVoltoLayer:IntegrationTesting',
)


REDTURTLE_VOLTO_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(REDTURTLE_VOLTO_FIXTURE,),
    name='RedturtleVoltoLayer:FunctionalTesting',
)


REDTURTLE_VOLTO_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        REDTURTLE_VOLTO_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE,
    ),
    name='RedturtleVoltoLayer:AcceptanceTesting',
)


class RedturtleVoltoRestApiLayer(PloneRestApiDXLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        super(RedturtleVoltoRestApiLayer, self).setUpZope(
            app, configurationContext
        )

        self.loadZCML(package=collective.folderishtypes)
        self.loadZCML(package=collective.volto.cookieconsent)
        self.loadZCML(package=plone.restapi)
        self.loadZCML(package=redturtle.volto)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'redturtle.volto:default')


REDTURTLE_VOLTO_API_FIXTURE = RedturtleVoltoRestApiLayer()
REDTURTLE_VOLTO_API_INTEGRATION_TESTING = IntegrationTesting(
    bases=(REDTURTLE_VOLTO_API_FIXTURE,),
    name="RedturtleVoltoRestApiLayer:Integration",
)

REDTURTLE_VOLTO_API_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(REDTURTLE_VOLTO_API_FIXTURE, z2.ZSERVER_FIXTURE),
    name="RedturtleVoltoRestApiLayer:Functional",
)
