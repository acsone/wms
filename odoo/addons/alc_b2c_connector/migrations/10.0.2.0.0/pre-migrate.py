# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    ApiKey = env["auth.api.key"]
    api_keys_by_name = {a.name: a for a in ApiKey.search([])}
    for module, name in [
        ("alc_chronovet", "chronovet_rest_api"),
        ("alc_placedesvetos", "place_des_vetos_rest_api"),
        ("alc_clubvetshop", "clubvetshop_rest_api"),
    ]:
        api_key = api_keys_by_name.get(name)
        if not api_key:
            _logger.info("No api key record found for %s", name)
            continue
        xml_id = "api_key_" + name
        if env.ref("{}.{}".format(module, xml_id), raise_if_not_found=False):
            continue
        _logger.info("Creating xmlid for auth.api.key %s", name)
        env["ir.model.data"].create(
            {
                "module": module,
                "name": xml_id,
                "model": api_key._name,
                "res_id": api_key.id,
            }
        )
