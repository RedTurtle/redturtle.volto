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
- **Document** are now folderish
- **Plone Site** is a DX content

Blocks
------

**volto.blocks** behavior is enabled by default for these content-types:

- Document
- News Item
- Event

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


Installation
------------

Install redturtle.volto by adding it to your buildout::

    [buildout]

    ...

    eggs =
        redturtle.volto


and then running ``bin/buildout``


Contribute
----------

- Issue Tracker: https://github.com/RedTurtle/redturtle.volto/issues
- Source Code: https://github.com/RedTurtle/redturtle.volto


License
-------

The project is licensed under the GPLv2.

Authors
-------

This product was developed by **RedTurtle Technology** team.

.. image:: https://avatars1.githubusercontent.com/u/1087171?s=100&v=4
   :alt: RedTurtle Technology Site
   :target: http://www.redturtle.it/
