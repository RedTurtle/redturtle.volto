Changelog
=========

5.9.1 (unreleased)
------------------

- Fix in resolveuid serializer if block is not a dict nor dict-like 
  [mamico]
- Make querystringsearch endpoint more customizable: now custom_query is defined in a separate method.
  [cekk]
- fix file:/// as external link in summary
  [mamico]

5.9.0 (2025-06-26)
------------------

- Fix rss feed image selection, now it uses the correct field for preview_image.
  [mamico]
- Fix issue with event search in @querystring-search override:
  converting a timezone-aware DateTime to utcdatetime causes a problem when searching for
  "today", as it shifts start=day x at 00:00 to start=day x-1 at 22:00 in GMT+2 timezone.
  [lucabel]
- Handle sort_on also when using AdvancedQuery.
  [cekk]
- Remove z3c.jbot compatibility and customize templates in standard-way.
  [cekk]
- Force indexing subjects in SearchableText with ICategorization to keep the old Plone functionality (remove this when the official pr is merged).
  [cekk]
- Enable kitconcept.seo behavior on Site Root.
  [cekk]

5.8.0 (2025-03-20)
------------------

- Add linkintegrity retriever for Link objects so when the referred object will be deleted, linkintegrity check will be raised also for Links.
  [cekk]


5.7.1 (2025-03-13)
------------------

- Customize serialzier for repeatableContentBlock.
  [cekk]
- Include experimental.noacquisition in the config.
  Needed for pip buidls.
  [folix-01]


5.7.0 (2025-02-06)
------------------

- Add experimental.noacquisition as dependency.
  [cekk]
- Patch absolutize_path method to disable acquisition when checking aliases.
  [cekk]
- Update it translations
  [lucabel]


5.6.3 (2024-12-02)
------------------

- Add patch for blocksRetriever.
  [eikichi18]
- Enable blocks linkintegrity on Site Root too.
  [cekk]

5.6.2 (2024-11-28)
------------------

- Add patch for SlateBlockslinkRetriever.
  [eikichi18]


5.6.1 (2024-11-21)
------------------

- Add linkintegrity check also for count_down block.
  [cekk]


5.6.0 (2024-11-21)
------------------

- Add linkintegrity indexers for some custom blocks.
  [cekk]


5.5.7 (2024-10-28)
------------------

- Refactored AdvancedQuery part in @search endpoint to be more extendable.
  [cekk]


5.5.6 (2024-10-17)
------------------

- Remove dependency with *collective.volto.cookieconsent*.
  [cekk]
- Add more block indexers for SearchableText.
  [cekk]

5.5.5 (2024-09-23)
------------------

- Avoid acquisition in find-broken-links view when checking blocks.
  [cekk]


5.5.4 (2024-09-23)
------------------

- Fix typo in filename generation in "find-broken-links" view.
  [cekk]


5.5.3 (2024-09-23)
------------------

- Add view "find-broken-links" that return a csv file with a list of contents with broken links in blocks.
  [cekk]


5.5.2 (2024-09-05)
------------------

- Fix SummarySerializer for collection exporting
  Links
  [lucabel]
- remove newsitem template override, use default dexterity view for newsitem in backend
  [mamico]
- Customize @@display-file to allow to download files with proper filename.
  [cekk]
- Add "type" to EXCLUDE_KEYS in blocks serializer/deserializer to not convert this slate attribute.
  [cekk]

5.5.1 (2024-07-22)
------------------

- Allow to select which image miniature use in
  RSS
  [lucabel]


5.5.0 (2024-07-10)
------------------

- Fixed limit event occurrences to 100.
  [eikichi18]
- Add dependency with collective.volto.sitesettings.
  [cekk]


5.4.9 (2024-04-22)
------------------

- Limit event occurrences to 100.
  [mamico]
- Customize INameChooser adapter to check also alias ids and disallow to create contents that could override aliases.
  [cekk]
- Customize also `copy` and `move` endpoints to raise BadRequest if that action will override some aliases.
  [cekk]
- Add flag in controlpanel to enable/disable INameChooser customization.
  [cekk]
- Exclude bg_color from transformed fields in deserializer.
  [cekk]
- Uninstall collective.volto.cookieconsent (deprecated). Will be removed from dependencies in next releases.
  [cekk]
- Add dependency to collective.volto.gdprcookie and install it by default.
  [cekk]

5.4.8 (2024-03-19)
------------------

- Do not try to convert strings in internal paths for *form* blocks.
- Handle None values in link integrity blocks adapter.
- Patch in @querystring-search that avoid to search through all the site if there is an absolutePath criteria with non existing UID and b_size==1.
  See #99 for more details.
  [cekk]


5.4.7 (2024-03-11)
------------------

- Add adapter handler for event in rss feed to export
  start date instead of publication date
  [lucabel]


5.4.6 (2024-03-06)
------------------

- Added check if value is a dict before using get method.
  [eikichi18]


5.4.5 (2024-03-05)
------------------

- Update plone.restapi requirement to 9.6.0 version
  [folix-01]
- Removed monkeypatch for plone.restartpi.serializer.utils.RESOLVEUID_RE
  [folix-01]

5.4.4 (2024-02-20)
------------------

- Add adapters for link integrity for content-types with BlocksField fields.
  [cekk]
- Fix: occurrences indexing
  [mamico]


5.4.3 (2024-01-30)
------------------

- Upgrade step to remove all custom Googlebot rules from robots.txt
  [mamico]

- Fix: add range_start to function for calculate recurrences in the right way
  [eikichi18]

5.4.2 (2024-01-11)
------------------

- Fix deserializer for relationfield, add lstrip to path object calculation
  [eikichi18]


5.4.1 (2023-12-28)
------------------

- Fix deserializer for relationfield, use UID instead of @id
  [eikichi18]

- Isort
  [folix-01]

- Add monkeypatch to fix @scadeziario-day endpoint
  [eikichi18]


5.4.0 (2023-11-14)
------------------

- Return error instead of raise Excpetion for BadRequest in querystringsearch
  [mamico]

- Add upgrade step and setuphandler to fix robots.txt
  original rules adding 'Allow: /*?expand*'
  [lucabel]

5.3.0 (2023-10-25)
------------------

- Fix: the 'fix-link' view has a bug that corrupts links by replacing
  the current external URL with a URL that is always relative to the
  site, even when requesting replacement with a link from a different
  website.
  [lucabel].

- plone.app.redirector.FourOhFourView.search_for_similar patch to enable conditionally
  the search for similar
  [folix-01]

- Set search/querystring-search limit patch only for anonymous users.
  Auth users can need to perform an higher query (in contents view for example).
  [cekk]

- Re-apply context UID filter in querystringsearch service (as it is in plone.restapi).
  [cekk]

5.2.4 (2023-09-26)
------------------

- Fix the issue in the @translation GET endpoint: If this
  endpoint is invoked, possibly by a bot, and plone.app.multilingual
  is not installed, the call will result in an empty search query
  on the catalog.
  [lucabel]

- backport https://github.com/plone/Products.CMFPlone/pull/3845
  fix: avoid searching all users when many_users is flagged
  [mamico]

5.2.3 (2023-09-21)
------------------

- Max search limit became configurable by env var 'REDTURTLE_VOLTO_MAX_LIMIT_SEARCH', 500 by default.
  [folix-01]


5.2.2 (2023-08-29)
------------------

- Fix RESOLVEUID_RE regexp.
  [cekk]


5.2.1 (2023-08-29)
------------------

- Use plone.volto uid_to_url method to convert resolveuid links in summary.
  [cekk]
- Patch plone.restapi RESOLVEUID_RE regexp to catch more urls.
  [cekk]
- Ignore non-existing indexes in custom ranking.
  [cekk]


5.2.0 (2023-08-21)
------------------

- Add catalog and search patches to limit results.
  [cekk]


5.1.0 (2023-08-17)
------------------

- set authorization bearer header from auth_token cookie
  [mamico]

- Remove Patch to avoid auto-closed tags in portal transforms: https://github.com/plone/Products.PortalTransforms/pull/43
  [mamico]

- Remove Patch for folderish types migration https://github.com/plone/plone.volto/pull/86
  [mamico]


5.0.1 (2023-07-04)
------------------

- Custom portal url in @@fix-links
  [mamico]


5.0.0 (2023-04-04)
------------------

- Remove unused default text in homepage.
  [cekk]


5.0.0rc1 (2023-03-20)
---------------------

- Plone 6.0 support

- Handle custom search ranking with AdvancedQuery.
  [mamico]

- Add controlpanel for redturtle.volto settings.
  [cekk]

4.1.3 (2023-02-12)
------------------

- sitemap.xml.gz customization.
  [mamico]


4.1.2 (2022-12-27)
------------------

- Customized voltobackendwarning viewlet because is broken in plone 5.2.
  [cekk]


4.1.1 (2022-12-23)
------------------

- Upgrade-step to remove etags list from p.a.caching terseCaching (in old Plone sites).
  [cekk]


4.1.0 (2022-11-22)
------------------

- Add new utility view `@@find-blocks`.
  [cekk]


4.0.2 (2022-08-29)
------------------

- Patch for plone.volto upgrade-step (https://github.com/plone/plone.volto/pull/86).
  [cekk]


4.0.1 (2022-08-12)
------------------

- Fix upgrade-step.
  [cekk]
- Allow add Document into News Item and Event.
  [cekk]


4.0.0 (2022-08-12)
------------------

- Remove content-types customizations to be aligned with plone.volto configs.
  [cekk]


3.12.2 (2022-05-19)
-------------------

- Add *query* to ignored keys in blocks deserializer. This avoid blocks with querystringsearch widget to be parsed (for example the search one).
  [cekk]

3.12.1 (2022-05-19)
-------------------

- Add string interp for volto_parent_url.
  [eikichi18]


3.12.0 (2022-04-04)
-------------------

- Add new metadata for Events dates.
  [cekk]


3.11.0 (2022-04-01)
-------------------

- Add stringinterp adapter to replace *{volto_url}* with the current frontend url (backend url without "/api").
  [cekk]


3.10.0 (2022-03-26)
-------------------

- Add Table block serializer/deserializer for internal links.
  [cekk]
- Add view for fix internal links.
  [cekk]


3.9.2 (2022-03-25)
------------------

- Fix remoteUrl serialization in summary.
  [cekk]


3.9.1 (2022-03-17)
------------------

- Refs serialization in blocks now uses brains instead adapted objects because brain has all catalog metadata and can get the fullobject.
  [cekk]


3.9.0 (2022-03-14)
------------------

- Allow to select custom miniature for RSS template
  [lucabel]
- Better serialize refs in blocks: now we don't serialize the full object, but only the summary (with all metadata) to decrease (A LOT) the size of the response.
  [cekk]

3.8.3 (2022-03-07)
------------------

- Fix null dates in summary serialization (now we handle differente use-cases).
  [cekk]
- Return remoteUrl metadata when serializing a brain for backward compatibility with non-brain serializers.
  [cekk]


3.8.2 (2022-02-07)
------------------

- Handle non-path values in blocks deserializer when trying to extract UIDs.
  [cekk]


3.8.1 (2022-01-31)
------------------

- Return null value in summary serialization for dates not set (because metadata are set with dates in the future or past for better filtering/sorting).
  [cekk]


3.8.0 (2022-01-26)
------------------

- Customized json summary serializer to expose image scales when requested _all metadata_fields without waking up the object.
  [cekk]


3.7.3 (2021-12-27)
------------------

- Upgrade-step to add default blocks in pages that don't have them.
  [cekk]


3.7.2 (2021-12-02)
------------------

- Customized ZCTextIndexQueryParser for https://github.com/plone/plone.restapi/pull/1209.
  [cekk]


3.7.1 (2021-12-01)
------------------

- Upgrade-step to reindex SearchableText for all contents with a table block (change in plone.restapi 8.16.1).
  [cekk]

3.7.0 (2021-12-01)
------------------

- Remove enabled_vocabularies implementation because in recent plone.restapi (>8.15.2) there is a standard way.
  [cekk]

3.6.2 (2021-11-09)
------------------

- Bypass plone.volto serialization for blocks right now (in monkeypatch.py).
  [cekk]


3.6.1 (2021-11-05)
------------------

- Fix upgrade-step for plone.volto.
  [cekk]


3.6.0 (2021-10-28)
------------------

- Add plone.volto dependency
  [cekk]


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
