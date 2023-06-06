# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    """Set the rounding on Units to 1."""
    category = env.ref("uom.product_uom_categ_unit")
    uoms = env["uom.uom"].search([("category_id", "=", category.id)])
    uoms.write({"rounding": 1.0})
