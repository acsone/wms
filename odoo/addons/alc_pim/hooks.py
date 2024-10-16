# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import csv
import logging
import os
from collections import defaultdict

import odoo

langs_alcyon = {"fr_BE", "nl_BE"}

_logger = logging.getLogger()


def pre_init_hook(cr):
    env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})
    Langs = env["res.lang"].with_context(active_test=False)
    for code in langs_alcyon:
        lang = Langs.search([("code", "=", code)])
        if not lang.active:
            lang.active = True
            env["ir.module.module"]._load_module_terms(["base"], [lang.code])


def post_init_hook(cr, registry=None):
    _load_attribute_options_translations(cr)
    _load_categories_translations(cr)


def _load_attribute_options_translations(cr):
    _logger.info("Load translations for attributes options")
    env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})
    path = os.path.join(os.path.dirname(__file__), "static", "alc_options.csv")
    with open(path, encoding="utf-8") as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=",")
        all_options_records = env["attribute.option"].search([])
        option_ids_by_en_name = defaultdict(list)
        for r in all_options_records:
            option_ids_by_en_name[r.name].append(r.id)
        for r in csv_reader:
            ids = option_ids_by_en_name.get(r["en_GB"])
            if not ids:
                continue
            records = env["attribute.option"].browse(ids)
            for lang in langs_alcyon:
                records.with_context(lang=lang).write({"name": r[lang]})


def _load_categories_translations(cr):
    _logger.info("Load translations for categories")
    env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})
    path = os.path.join(os.path.dirname(__file__), "static", "categories.csv")
    with open(path, encoding="utf-8") as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=";")
        all_categories_records = env["product.category"].search([("is_web", "=", True)])
        categorie_ids_by_en_name = defaultdict(list)
        for r in all_categories_records:
            categorie_ids_by_en_name[r.name].append(r.id)
        for r in csv_reader:
            ids = categorie_ids_by_en_name.get(r["fr_BE"])
            if not ids:
                _logger.info("%s not found", r["fr_BE"])
                continue
            records = env["product.category"].browse(ids)
            for lang in ["en_US", *list(langs_alcyon)]:
                records.with_context(lang=lang).write({"name": r[lang]})
