.. This README is meant for consumption by humans and pypi. Pypi can render rst files so please do not use Sphinx features.
   If you want to learn more about writing documentation, please check out: http://docs.plone.org/about/documentation_styleguide.html
   This text does not appear on pypi or github. It is a comment.

===============
redturtle.volto
===============

This is an helper package that setup a RedTurtle's Plone site ready to work with Volto.

Features
========

Content-types
-------------

- Disabled **Collection**
- **Document**, **News Item** and **Event** are folderish types (thanks to collective.folderishtypes.dx)
- News Item and Event can only contain **Links**, **Images** and **Files**
- **Plone Site** is a DX content
- Revert **News Item** and **Event** to be non-folderish (collective.folderishtypes.dx makes them folderish)

Blocks
------

**volto.blocks** behavior is enabled by default for these content-types:

- Document
- News Item
- Event

Links
-----

There is a custom adapter for TextLine field that return the proper widget for **remoteUrl**.

Custom blocks transformers
--------------------------

There are custom transformers for serializer and deserializer to better manage resolveuids.

There is an edge-case when a block refers its context: in this case, to avoid maximum recursion depth
in uids resolving, that uid will be expanded with the Summary json version and not the full object.


@context-navigation endpoint
----------------------------

plone.restapi's **@navigation** endpoint always return the navigation tree from the site root.

There is a **@context-navigation** endpoint that returns the contextual navigation tree:

    > curl -i http://localhost:8080/Plone/folder?context-navigation -H 'Accept: application/json'

This is the result::

    {
        '@id': 'http://localhost:8080/Plone/folder',
        'items': [
            {'@id': 'http://localhost:8080/Plone/folder/folder-a',
                'description': '',
                'title': 'Folder A'},
            {'@id': 'http://localhost:8080/Plone/folder/folder-b',
                'description': '',
                'title': 'Folder B'},
            {'@id': 'http://localhost:8080/Plone/folder/folder-c',
                'description': '',
                'title': 'Folder C'}
        ]
    }

By default only first level is shown.
You can pass an **expand.navigation.depth** parameter to set the depth::

    > curl -i http://localhost:8080/Plone/folder?context-navigation?expand.navigation.depth=2 -H 'Accept: application/json'

And this is the result::

    {
        '@id': 'http://localhost:8080/Plone/folder',
        'items': [
            {
                '@id': 'http://localhost:8080/Plone/folder/folder-a',
                'description': '',
                'items': [
                    {
                        '@id': 'http://localhost:8080/Plone/folder/folder-a/folder-aa',
                        'description': '',
                        'title': 'Folder AA',
                    },
                    {
                        '@id': 'http://localhost:8080/Plone/folder/folder-a/folder-ab',
                        'description': '',
                        'title': 'Folder AB',
                    },
                ],
                'title': 'Folder A',
            },
            {
                '@id': 'http://localhost:8080/Plone/folder/folder-b',
                'description': '',
                'title': 'Folder B',
            },
            {
                '@id': 'http://localhost:8080/Plone/folder/folder-c',
                'description': '',
                'title': 'Folder C',
            },
        ],
    }

@site-search endpoint
---------------------

This endpoint works exactly like **@search** but take care of types not searchable settings.


@sitemap-settings
-----------------

Endpoint that returns sitemap settings for anonymous users (that can't access registry entries).

Returns a data structure like this::

    {
        'depth': 3,
    }


@search endpoint
----------------

We customized @search endpoint for that bug: https://github.com/plone/plone.restapi/pull/1066

@events-search endpoint
-----------------------

Endpoint similar to `@querystring-search` that is used to make queries for events.

This uses `get_events` method to search events: that method handle recurrences and avoid wrong results.

The usage is similar to `@querystring-search`.


Disallow bot indexing
---------------------

There is a custom viewlet that add a <meta> tag in the <head> section to prevent bot indexing.

For reference: https://developers.google.com/search/docs/advanced/crawling/block-indexing?visit_id=637489966041845317-1328107746&rd=1

Patches
=======

Keywords vocabulary
-------------------

We copied the patch from kitconcept.volto_ for special characters in keywords vocabulary
(used for example in Subjects field).

.. _kitconcept.volto: https://github.com/kitconcept/kitconcept.volto/blob/master/src/kitconcept/volto/vocabularies/subject.py


Products.PortalTransforms
-------------------------

See https://github.com/plone/Products.PortalTransforms/pull/43

There is a monkeypatch to apply that changes.

Events recurrence
-----------------

There is a monkeypatch for Events recurrences that fix their duration.

If it works well, we can make a pr in p.a.event.


Respect locally allowed types on paste
--------------------------------------

Disallow paste items that are not allowed into destination folder.


Fixed dependencies versions
===========================

There are some dependencies fixed in setup.py file.
When Plone 5.2 will be released, we can remove these:

- waitress >= 1.4.3
- plone.app.contenttypes >= 2.1.6
- plone.rest >= 1.6.1
- plone.dexterity >= 2.9.5
- Products.ZCatalog >= 5.1
- plone.namedfile >= 5.4.0
- Products.PloneHotfix20200121 >= 1.0

New Criteria
============

There is one new criteria for Collections and Listing blocks that search on **exclude_from_nav** index.


Installation
============

Install redturtle.volto by adding it to your buildout::

    [buildout]

    ...

    eggs =
        redturtle.volto


and then running ``bin/buildout``


Contribute
==========

- Issue Tracker: https://github.com/RedTurtle/redturtle.volto/issues
- Source Code: https://github.com/RedTurtle/redturtle.volto


License
=======

The project is licensed under the GPLv2.

Authors
=======

This product was developed by **RedTurtle Technology** team.

.. image:: https://avatars1.githubusercontent.com/u/1087171?s=100&v=4
   :alt: RedTurtle Technology Site
   :target: http://www.redturtle.it/
