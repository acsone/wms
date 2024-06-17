# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


def _move_table(env):
    """Migrate data from former account_move_stock_picking_rel table to stock_picking_cash_on_delivery_move_id_rel."""
    if openupgrade.table_exists(env.cr, "account_move_stock_picking_rel"):
        _logger.info(
            "Move account_move_stock_picking_rel data TO stock_picking_cash_on_delivery_move_id_rel"
        )
        query = """
            INSERT INTO stock_picking_cash_on_delivery_move_id_rel (picking_id, move_id)
                SELECT stock_picking_id, account_move_id
                    FROM account_move_stock_picking_rel
                    WHERE NOT EXISTS (SELECT 1 FROM stock_picking_cash_on_delivery_move_id_rel WHERE picking_id = stock_picking_id AND move_id = account_move_id)
        """
        openupgrade.logged_query(env.cr, query)


def _move_conditions(env):
    """
    In partner_invoicing_mode_cash_on_delivery module, cash on delivery is set.

    on payment mode.

    Set partners in that case to 'Immediate' payment term and add a payment mode
    to cash on delivery.
    """
    partners = env["res.partner"].search(
        [
            (
                "property_payment_term_id",
                "=",
                env.ref("__setup__.account_payment_term_cr").id,
            )
        ]
    )
    partners.write(
        {
            "property_payment_term_id": env.ref(
                "account.account_payment_term_immediate"
            ).id,
            "customer_payment_mode_id": env.ref(
                "partner_invoicing_mode_cash_on_delivery.payment_mode_cash_on_delivery"
            ).id,
        }
    )


def _deactivate_cash(env):
    env.ref("__setup__.account_payment_term_cr").write({"active": False})


@openupgrade.migrate()
def migrate(env, version):
    _move_table(env)
    _move_conditions(env)
    _deactivate_cash(env)
