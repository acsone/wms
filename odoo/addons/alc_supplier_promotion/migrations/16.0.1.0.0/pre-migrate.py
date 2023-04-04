# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


def migrate(cr, version):
    # Moved fields from alc_b2c_connector
    openupgrade.update_module_moved_fields(
        cr,
        "product.supplierinfo",
        [
            "is_null_date_start",
            "discount_sale",
            "min_qty_sale",
            "min_qty",
        ],
        "pricelist_discount",
        "alc_supplier_promotion",
    )
