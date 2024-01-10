from odoo.tools import sql


def migrate(cr, version=None):
    if sql.column_exists(cr, "res_users", "only_one_delivery_round_by_cluster"):
        sql.rename_column(
            cr,
            "res_users",
            "only_one_delivery_round_by_cluster",
            "only_one_release_channel_by_picking_batch",
        )
    if sql.column_exists(cr, "shopfloor_menu", "restrict_to_same_release_channel"):
        sql.rename_column(
            cr,
            "shopfloor_menu",
            "restrict_to_same_release_channel",
            "release_channel_required",
        )
