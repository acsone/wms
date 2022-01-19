# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import os

import unicodecsv as csv

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


def post_init_hook(cr):
    _load_attribute_options_translations(cr)


def _load_attribute_options_translations(cr):
    env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})
    path = os.path.join(os.path.dirname(__file__), "static", "alc_options.csv")
    with open(path) as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=",")
        all_options_records = env["attribute.option"].search([])
        options_by_en_name = {r.name: r for r in all_options_records}
        for r in csv_reader:
            record = options_by_en_name[r["en_GB"]]
            for lang in langs_alcyon:
                record.with_context(lang=lang).write({"name": r[lang]})
