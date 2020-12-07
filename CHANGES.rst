Changelog
=========


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
