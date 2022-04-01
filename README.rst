.. This README is meant for consumption by humans and pypi. Pypi can render rst files so please do not use Sphinx features.
   If you want to learn more about writing documentation, please check out: http://docs.plone.org/about/documentation_styleguide.html
   This text does not appear on pypi or github. It is a comment.

===============
redturtle.volto
===============

This is an helper package that setup a RedTurtle's Plone site ready to work with Volto.


|python| |version| |ci|

.. |python| image:: https://img.shields.io/pypi/pyversions/redturtle.volto.svg
  :target: https://pypi.python.org/pypi/redturtle.volto/

.. |version| image:: http://img.shields.io/pypi/v/redturtle.volto.svg
  :target: https://pypi.python.org/pypi/redturtle.volto

.. |ci| image:: https://github.com/RedTurtle/redturtle.volto/actions/workflows/tests.yml/badge.svg
  :target: https://github.com/RedTurtle/redturtle.volto/actions

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

There are also some adapters registered for **IBlockSearchableText** to index some common blocks.

Links
-----

There is a custom adapter for TextLine field that return the proper widget for **remoteUrl**.

Custom blocks transformers
--------------------------

There are custom transformers for serializer and deserializer to better manage resolveuids.

If a block refers to some internal content, on deserialization we only store its UID, and in serialization
we "expand" informations with the summary-serialized content.

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

@querystring-search endpoint customization
------------------------------------------

If we are searching only for `Event` types, do a special search using **get_events** method to search events: that method handle recurrences and avoid wrong results.

Otherwise, perform a default querystring-search.


Disallow bot indexing
---------------------

There is a custom viewlet that add a <meta> tag in the <head> section to prevent bot indexing.

For reference: https://developers.google.com/search/docs/advanced/crawling/block-indexing?visit_id=637489966041845317-1328107746&rd=1

Patches
=======

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


DateTime field serializer/deserializer
--------------------------------------

Customized these adapters to correctly set effective and expires dates.

Without this change, these dates will be stored with UTC hour and not with the current timezone's hour
because behavior's `setter/getter <https://github.com/plone/plone.app.dexterity/blob/master/plone/app/dexterity/behaviors/metadata.py#L278>`_ strip timezone from the value.

With this patch we will send to the setter the date with already localized hour, so even if the setter strip timezone info, we are going to save the correct date.

Default ISerializeToJsonSummary adapter
---------------------------------------

This is a patch for backward compatibility for old volto templates that need a full image scales object.


New Criteria
============

There is one new criteria for Collections and Listing blocks that search on **exclude_from_nav** index.


Caching controlpanel
====================

After installation the caching control panel is populated with custom policies while caching is globally enabled by default. Please, set the caching proxies properly.
 

@vocabularies permissions
=========================

According to new plone.restapi implementation, @vocabularies endpoint will check some permissions to make a vocabulary available or not.

We patched PERMISSIONS variable in __init__ file to allow Keywords vocabulary to be available for anonymous users.

Reference: https://github.com/plone/plone.restapi/pull/1258#issuecomment-980628982

RamCache in tersecaching
------------------------

We disabled ramcache for tersecaching (plone.app.caching.terseCaching.plone.content.dynamic.ramCache) because
it seems not correctly purged when there are more instances and a content has been modified.

We need to check why it's not purged and fix it.


Template overrides
==================

RSS.pt Template
---------------
There is a customization of the Products.CMFPlone.browser.syndication.templates.RSS.pt
template to add enclosure tag to feed items.
A record has also been added to the registry to be able to set the miniature to be
displayed with the RSS item. This record is named redturtle.volto.rss_image_miniature

Fix internal links
==================

There is a view **@@fix-links** that will check internal links into blocks and fix some links that refs to a staging
or local development environment.


Stringinterp adapters
=====================

There is a new stringinterp adapter that can be used for example in content rules: **{volto_url}**

This adapter will remove "/api" from the content's absolute_url.

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
