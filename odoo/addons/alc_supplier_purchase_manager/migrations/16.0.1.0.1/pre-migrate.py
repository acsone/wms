# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _add_supplier_user(env):
    """Add the purchase manager user on purchase orders."""
    field_spec = [
        (
            "purchase_manager_id",
            "purchase.order",
            False,
            "many2one",
            "integer",
            "alc_supplier_purchase_manager",
        )
    ]
    openupgrade.add_fields(env, field_spec)

    query = """
        UPDATE purchase_order po
            SET purchase_manager_id = rp.purchase_manager_id
            FROM
            res_partner rp
            WHERE rp.id = po.partner_id
            AND po.state NOT IN ('done', 'cancel')
    """
    openupgrade.logged_query(env.cr, query)


@openupgrade.migrate()
def migrate(env, version):
    _add_supplier_user(env)
