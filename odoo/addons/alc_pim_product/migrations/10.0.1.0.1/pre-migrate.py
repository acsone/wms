# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


def migrate(cr, version):
    # Moved xml_id to alc_pim_product
    to_renames = []
    for xid in [
        "attribute_size_clothing_option_id",
        "attribute_thread_option_id",
        "attribute_food_range_option_id",
        "attribute_presentation_option_id",
        "attribute_categ_age_option_ids",
        "attribute_product_color_option_ids",
        "attribute_indication_option_ids",
        "attribute_animal_size_option_ids",
        "attribute_active_principle_option_ids",
        "attribute_administration_route_option_ids",
    ]:
        to_renames.append(("alc_pim." + xid, "alc_pim_product." + xid))
    openupgrade.rename_xmlids(cr, to_renames)
