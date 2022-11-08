# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import SUPERUSER_ID, api


def _get_alc_version(cr, memo={}):  # noqa # pylint: disable=dangerous-default-value
    if "alc" not in memo:
        env = api.Environment(cr, SUPERUSER_ID, {})
        memo["alc"] = env["ir.config_parameter"].get_param("ribbon.name", default="dev")
    return memo["alc"]
