# -*- coding: utf-8 -*-
from Products.Five import BrowserView
from plone import api
from Acquisition import aq_base
from plone.dexterity.utils import iterSchemata
from zope.schema import getFieldsInOrder
from plone.restapi.interfaces import IFieldDeserializer
from zope.component import queryMultiAdapter

import logging
import re
import json

logger = logging.getLogger(__name__)


class View(BrowserView):

    results = {}

    def __call__(self):
        submitted = self.request.form.get("confirm", None)
        dry_mode = self.request.form.get("dry_mode", False)
        to_replace = self.request.form.get("to_replace", "")
        if not submitted and not to_replace:
            return super().__call__()
        portal_catalog = api.portal.get_tool("portal_catalog")
        results = portal_catalog()
        tot = len(results)
        i = 0
        fixed_objects = []
        not_fixed_objects = []
        logger.info("## START ##")
        for brain in results:
            if (i + 1) % 200 == 0:
                logger.info(" - Progress {}/{}".format(i + 1, tot))
            item = brain.getObject()
            aq_base_obj = aq_base(item)
            for schemata in iterSchemata(aq_base_obj):
                for name, field in getFieldsInOrder(schemata):
                    if name in ["blocks_layout"]:
                        continue
                    value = getattr(aq_base_obj, name, None)
                    if isinstance(value, str):
                        res = self.check_broken_value(
                            value=value, is_link=brain.portal_type == "Link"
                        )
                    elif isinstance(value, dict):
                        res = self.check_broken_blocks_links(
                            blocks=value, context=item, field=field
                        )
                    else:
                        continue
                    if res["ok"]:
                        continue
                    res_data = {
                        "url": brain.getURL(),
                        "field": name,
                        "old": self.format_value(value),
                        "new": self.format_value(res["new_value"]),
                    }
                    if res["fixed"]:
                        fixed_objects.append(res_data)
                    else:
                        not_fixed_objects.append(res_data)
                    if not dry_mode:
                        # set the new value anyway because some values could not be transformed,
                        # but they now have the right url anyway.
                        setattr(item, name, res["new_value"])
            i += 1
        logger.info("### END ###")
        logger.info("### {} items fixed ###".format(len(fixed_objects)))
        logger.info("### {} items NOT fixed ###".format(len(not_fixed_objects)))

        if dry_mode:
            api.portal.show_message(
                message="Dry-mode selected. Nothing wrote on database.",
                request=self.request,
            )
        else:
            api.portal.show_message(message="Values updated", request=self.request)
        self.results = {"fixed": fixed_objects, "not_fixed": not_fixed_objects}
        return super().__call__()

    def format_value(self, value):
        if isinstance(value, dict):
            return json.dumps(value, indent=4)
        return value

    def check_pattern(self, value):
        for url in self.request.form.get("to_replace", "").split():
            if url in value:
                return True

    def replace_pattern(self, value, is_link=False):
        for url in self.request.form.get("to_replace", "").split():
            match = re.search(r"(?<={}).*".format(url), value)
            if match:
                try:
                    path = match.group()
                    obj = api.content.get(path)
                except Exception as e:
                    logger.exception(e)
                    logger.warning("Ignoring: {}".format(value))
                    return value
                if obj:
                    if is_link:
                        return "${portal_url}/resolveuid/" + obj.UID()
                    else:
                        return obj.UID()
        return value

    def check_broken_blocks_links(self, blocks, field, context):
        res = {"ok": True}
        try:
            data = json.dumps(blocks)
        except Exception:
            return res
        if self.check_pattern(value=data):
            res["ok"] = False
            res["fixed"] = True
            portal_url = self.context.portal_url()
            # convert broken links to current site ulr and then deserialize all
            # blocks to have the right values
            for url in self.request.form.get("to_replace", "").split():
                data = data.replace(url, portal_url)
            deserializer = queryMultiAdapter(
                (field, context, self.request), IFieldDeserializer
            )
            new_value = deserializer(json.loads(data))
            new_value_json = json.dumps(new_value)
            for url in self.request.form.get("to_replace", "").split():
                if url in new_value_json:
                    res["fixed"] = False
            res["new_value"] = new_value
        return res

    def check_broken_value(self, value, is_link=False):
        res = {"ok": True}
        if self.check_pattern(value=value):
            res["ok"] = False
            new_val = self.replace_pattern(value=value, is_link=is_link)
            if new_val == value:
                res["fixed"] = False
            else:
                res["fixed"] = True
            res["new_value"] = new_val
        return res
