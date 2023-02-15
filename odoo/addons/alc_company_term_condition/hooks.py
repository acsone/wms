# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def pre_init_hook(cr):
    openupgrade.update_module_moved_fields(
        cr,
        "res.company",
        [
            "order_phone",
            "order_fax",
            "invoice_terms_conditions",
            "delivery_terms_conditions",
        ],
        "specific_base",
        "alc_company_term_condition",
    )
