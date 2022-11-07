# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    if not version:
        return
    env = api.Environment(cr, SUPERUSER_ID, {})
    # all models that inherit mixin.file_id
    model_names = ["alc.eshop.ads", "alc.classified", "alc.eshop.cms.news"]
    domain = [("is_past", "=", False), ("filename", "in", [False, ""])]
    for model_name in model_names:
        records = env[model_name].search(domain)
        for record in records:
            record.filename = record.file_id.name
