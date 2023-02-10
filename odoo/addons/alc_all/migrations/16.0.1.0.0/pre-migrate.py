# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo.tools import sql

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    addons_to_uninstall = [
        "alc_product_picking_zone",
        "alc_product_storage_type_tracking",
        "alc_stock_location_content_relocation",
        "alc_stock_move_operation",
        "alc_stock_pack_operation_audit",
        "alc_stock_picking_number_package",
        "alc_stock_picking_package",
        "alc_stock_picking_policy_block",
        "alc_stock_quant_package_delivery",
        "alc_stock_quant_package_nbr",
        "alc_stock_storage_type_fixed_location",
        "delivery_carrier_label_gls_server_env",
        "partner_delivery",
        "partner_helper",
        "product_packaging_barcode",
        "purchase_unlink_cancelop",
        "specific_zetes",
        "stock_expired",
        "stock_inventory_controller",
        "stock_inventory_products",
        "stock_location",
        "stock_location_notranslate",
        "stock_location_report",
        "stock_operation_cleaner",
        "stock_operation_recompute",
        "stock_reassign_auto",
        "stock_picking_assignment",
        "stock_picking_backorder",
        "stock_picking_fillwithstock",
        "stock_picking_show_backorder",
        "stock_putaway_route",
        "base_cached_xmlid",
        "specific_data",
        "pricelist_discount",
        "stock_picking_subcode",  # replaced by stock_move_picking_type_origin
    ]
    for addon in addons_to_uninstall:
        _logger.info("uninstall %s", ",".join(addon))
        cr.execute(
            "update ir_module_module set state = 'to remove' where name = %s",
            (addon,),
        )
    _migrate_stock_picking_assignment(cr)


def _migrate_stock_picking_assignment(cr):
    _logger.info("picking_assignment: copy operator_id into user_id")
    if sql.column_exists(cr, "stock_picking", "operator_id"):
        cr.execute(
            """
            UPDATE stock_picking
            SET user_id = operator_id
            WHERE operator_id IS NOT NULL
            """
        )
        _logger.info("picking_assignment: drop operator_id")
        cr.execute("ALTER TABLE stock_picking DROP COLUMN operator_id")
