from . import models


def pre_init_hook(cr):
    cr.execute("ALTER TABLE stock_valuation_layer ADD COLUMN picking_type_id integer")
    cr.execute("ALTER TABLE stock_valuation_layer ADD COLUMN picking_type_code VARCHAR")
    cr.execute(
        "ALTER TABLE stock_valuation_layer ADD COLUMN operation_direction VARCHAR"
    )
    cr.execute(
        """
        UPDATE stock_valuation_layer
        SET picking_type_id=move.picking_type_id
        FROM stock_move AS move
        WHERE move.id=stock_valuation_layer.stock_move_id
        """
    )
    cr.execute(
        """
        UPDATE stock_valuation_layer
        SET picking_type_code=picking_type.code
        FROM stock_picking_type AS picking_type
        WHERE picking_type.id=stock_valuation_layer.picking_type_id
        """
    )
    cr.execute(
        """
        UPDATE stock_valuation_layer
        SET operation_direction='in'
        WHERE quantity > 0
        """
    )
    cr.execute(
        """
        UPDATE stock_valuation_layer
        SET operation_direction='out'
        WHERE quantity < 0
        """
    )
