Changelog
=========

3.5.0 (2021-10-11)
------------------

- p.a.caching rules for rest api services
  [mamico]

3.4.2 (2021-10-01)
------------------

- Fix tests.
  [cekk]

3.4.1 (2021-09-30)
------------------

- Disable ramcache from tersecaching (to fix the problem with cache invalidation for balanced instances..see README).
  [cekk]


3.4.0 (2021-09-29)
------------------

- Better handle events searches.
  [cekk]


3.3.0 (2021-09-21)
------------------

- Index text from some common blocks.
  [cekk]
- Fix date timezones in fields.
  [cekk]


3.2.2 (2021-08-24)
------------------

- Customize serializer/deserializer for DateTime fields to correctly set effective and expires with right timezone delta.
  [cekk]
- Enable Anonymous to access Plone vocabularies with restapi. **@vocabularies** endpoint has been customized to limit the vocabularies that anonymous can actually access.
  [cekk]

3.2.1 (2021-08-04)
------------------

- Remove customized @workflow endpoint. Is now merged in plone.restapi >= 8.7.1.
  [cekk]

3.2.0 (2021-08-02)
------------------

- Customize @workflow endpoint for plone.restapi #1184 and #1190 pr.
  [cekk]
- Remove default cache proxy address on install.
  [cekk]


3.1.3 (2021-06-30)
------------------

- Fix b_size conversion in upgrade-step for Volto 13.
  [cekk]

3.1.2 (2021-06-18)
------------------

- Fix also linkMore in volto13 migration.
  [cekk]


3.1.1 (2021-06-17)
------------------

- Handle contents with old Richtext values in volto13 migration.
  [cekk]



3.1.0 (2021-06-17)
------------------

- [BREAKING CHANGE] Volto 13 support. The upgrade-step will update listing blocks data.
  [cekk]


3.0.1 (2021-06-08)
------------------

- review caching profile
  [mamico]

3.0.0 (2021-05-28)
------------------

- Provided basic setup for caching policies in control panel.
  [daniele]

2.1.2 (2021-05-11)
------------------

- Additional fix in start and end values handling in querystring-search.
  [cekk]


2.1.1 (2021-05-11)
------------------

- Fix start and end values handling in querystring-search.
  [cekk]


2.1.0 (2021-05-05)
------------------

- Compatibility with changes in plone.restapi 7.3.2.
  [cekk]


2.0.2 (2021-05-05)
------------------

- Handle also limit in querystringsearch patch.
  [cekk]

2.0.1 (2021-05-05)
------------------

- Handle sort order in querystringsearch patch.
  [cekk]


2.0.0 (2021-04-30)
------------------

- Remove @events-search endpoint and customize @querystring-search one to handle Events like @events-search.
  [cekk]


1.3.0 (2021-04-19)
------------------

- Monkeypatch to respect locally allowed types also on content paste.
  [cekk]


1.2.4 (2021-04-15)
------------------

- Customize translation for remoteUrl field description only for restapi call.
  [cekk]


1.2.3 (2021-04-01)
------------------

- added block type 'searchEvents' to EXCLUDE_TYPES [giuliaghisini]


1.2.2 (2021-03-25)
------------------

- Added upgrade step to import p.a.c. profile.
  [daniele]

1.2.1 (2021-03-17)
------------------

- Monkeypatch for Events recurrences.
  [cekk]
- Fix profile name in upgrade-steps.
  [cekk]

1.2.0 (2021-03-02)
------------------

- New endpoint to search Events: @events-search.
- Better handle serialization for recursion problems: now only serialize with ISerializeToJsonSummary
  if the referred item is the current context.
  [cekk]


1.1.0 (2021-03-01)
------------------

- Expand uids with ISerializeToJsonSummary and not with fullobject to gain space and
  avoid maximum recursion depth it a block has an internal reference to the current context.
  [cekk]


1.0.9 (2021-02-23)
------------------

- Handle unauthorized in blocks serializer.
  [cekk]


1.0.8 (2021-02-19)
------------------

- Fix typo.
  [cekk]


1.0.7 (2021-02-19)
------------------

- Do not run dependencies when upgrading plone.app.registry.
  [cekk]

1.0.6 (2021-02-15)
------------------

- Disallow Plone site indexing: add noindex in <head>
  [cekk]
- Revert robots.txt customization because is in conflict to noindex directive.
  [cekk]

1.0.5 (2021-02-11)
------------------

- Custom @search endpoint to fix bug with Access inactive portal content permission
  (https://github.com/plone/plone.restapi/pull/1066)
  [cekk]


1.0.4 (2021-02-10)
------------------

- Customize robots.txt to disallow /api entry.
  [cekk]

1.0.3 (2021-02-09)
------------------

- Patched Products.PortalTransforms
  (https://github.com/plone/Products.PortalTransforms/pull/43).
  [cekk]



1.0.2 (2021-02-09)
------------------

- Re-add remoteUrl field serializer.
  [cekk]


1.0.1 (2021-02-08)
------------------

- [new] Add here from modena the RSS.pt template override
  [lucabel]
- Remove text block serializer that is already merged into plone.restapi.
  [cekk]
- Register generic serializer also for site root.
  [cekk]

1.0.0 (2020-12-07)
------------------

- Add exclude_from_nav as Collection criteria (used also in Volto's listing blocks).
  [cekk]
- Add custom TextLine adapter to return the proper widget for **remoteUrl** field.
  [cekk]

0.1.6 (2020-11-25)
------------------

- Allow Products.PloneHotfix20200121 versions greater than 1.0.
  [pnicolli]
- Fix generic serializer/deserializer.
  [cekk]
- Skip also "calendar" when check for url deserializing blocks
  [lucabel]
- Fix document template.
  [cekk]

0.1.5 (2020-10-20)
------------------

- Remove resolveuid serializer/deserializer for blocks: now they are integrated in plone.restapi.
  [cekk]
- Add custom transformers for blocks to handle link in generic blocks.
  [cekk]
- Enable Editor and Contributor to access Plone vocabularies with restapi.
  [cekk]
- Add @sitemap-settings endpoint.
  [cekk]

0.1.4 (2020-07-16)
------------------

- Add keywords vocabulary patch.
  [cekk]


0.1.3 (2020-06-22)
------------------

- Added default homepages
  [nzambello]
- Added blocks behavior to LRF
  [nzambello]
- Made editable and viewable Plone Site with blocks behavior
  [nzambello]
- Remove richtext behavior from News Items, Events and Documents.
  [cekk]
- News Item and Event are folderish and can only contain Links, Images and Files.
  [cekk]

0.1.2 (2020-05-25)
------------------

- Revert to Event and News Item default behaviors.
  [cekk]


0.1.1 (2020-05-22)
------------------

- Install also collective.volto.cookieconsent.
  [cekk]


0.1.0 (2020-05-22)
------------------

- Initial release.
  [cekk]
