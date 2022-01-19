# -*- coding: utf-8 -*-
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


def pre_init_hook(cr):
    # Moved xml_id to alc_sale_invoicing_policy
    to_renames = []
    for xid in [
        "management_attribute_group",
        "logistics_attribute_group",
        "marketing_attribute_group",
        "media_attribute_group",
        "commercial_attribute_group",
        "technical_attribute_group",
        "other_attribute_group",
        "attribute_set_medicaments",
        "attribute_set_aliments",
        "attribute_set_materiel",
    ]:
        to_renames.append(("alc_pim." + xid, "alc_pim_attribute_group." + xid))
    openupgrade.rename_xmlids(cr, to_renames)
