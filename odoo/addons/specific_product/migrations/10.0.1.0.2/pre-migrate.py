# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openupgradelib.openupgrade import update_module_moved_fields


def migrate(cr, version):
    old_module = "specific_product"
    new_module = "alc_product_pharmacy"
    models = ["product.template", "product.product", "delivery.carrier"]
    moved_fields = ["cnk_code", "belgium_only", "veterinary_only"]
    for model in models:
        update_module_moved_fields(cr, model, moved_fields, old_module, new_module)
