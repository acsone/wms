# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    groups = (
        env["stock.picking"].search([("state", "not in", ("done", "cancel"))]).group_id
    )
    for group in groups:
        pickings = group.picking_ids
        all_sales = pickings.move_ids.sale_line_id.order_id
        # approximation, only new orders will have the correct
        # links
        group.sale_ids |= all_sales
