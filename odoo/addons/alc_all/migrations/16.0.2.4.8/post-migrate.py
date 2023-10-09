# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # Change the loss location to the old one
    warehouse = env.ref("stock.warehouse0")
    location = warehouse.loss_location_id
    warehouse.loss_location_id = env.ref("stock_lot_loss.stock_location_14019")
    location.unlink()
    query = """
        DELETE FROM ir_model_data
            WHERE name = 'stock_location_14019'
            AND module = 'stock_lot_loss'
    """
    openupgrade.logged_query(env.cr, query)

    # Change the loss type to the old one
    loss_type = warehouse.loss_type_id
    warehouse.loss_type_id = env.ref("stock_lot_loss.stock_picking_type_23")
    loss_type.unlink()
    query = """
        DELETE FROM ir_model_data
            WHERE name = 'stock_picking_type_23'
            AND module = 'stock_lot_loss'
    """
    openupgrade.logged_query(env.cr, query)

    warehouse.loss_type_id.update(
        {
            "sequence_id": env.ref("stock_lot_loss.ir_sequence_rup").id,
            "sequence_code": "RUP",
        }
    )
    query = """
        DELETE FROM ir_model_data
            WHERE name = 'ir_sequence_rup'
            AND module = 'stock_lot_loss'
    """
    openupgrade.logged_query(env.cr, query)
