# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import odoo

langs_alcyon = {"fr_BE", "nl_BE"}


def pre_init_hook(cr):
    env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})
    Langs = env["res.lang"].with_context(active_test=False)
    for code in langs_alcyon:
        lang = Langs.search([("code", "=", code)])
        if not lang.active:
            lang.active = True
            env["ir.translation"].load_module_terms(["base"], [lang.code])
