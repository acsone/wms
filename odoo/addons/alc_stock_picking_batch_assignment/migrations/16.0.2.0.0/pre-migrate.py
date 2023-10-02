# Copyright 2023 ACSONE SA/NV


def migrate(cr, version):
    cr.execute(
        "delete from ir_ui_view where name = 'stock.picking.batch.form (in alc_stock_picking_batch_assignment)'"
    )
