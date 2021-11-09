# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import SUPERUSER_ID, api


def post_init_hook(cr, registry):
    mapping = {
        None: "other",
        "specific_partner.partner_category_veterinary": "veterinary",
        "specific_partner.partner_category_pharmacy": "wholesaler_pharmacy",
        "specific_partner.partner_category_callcenter": "wholesaler_veterinary",
        "specific_partner.partner_category_customerexport": "export_customer",
        "specific_partner.partner_category_student": "student_like",
        "specific_partner.partner_category_alcyonaire": "shareholder",
        "specific_partner.partner_category_med_export": "export_meds",
        "specific_partner.partner_category_only_material": "equipment_only",
        "specific_partner.partner_category_supplier": "supplier",
    }
    env = api.Environment(cr, SUPERUSER_ID, {})
    for xml_id, partner_type in mapping.items():
        alcyon_category_id = env.ref(xml_id).id if xml_id else xml_id
        q = "UPDATE res_partner SET partner_type = %s WHERE alcyon_category_id = %s"
        cr.execute(q, (partner_type, alcyon_category_id))
