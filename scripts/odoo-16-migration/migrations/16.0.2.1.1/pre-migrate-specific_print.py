# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.update_module_moved_fields(
        env.cr,
        "res.partner",
        [
            "is_price_on_labels",
            "no_labels_products",
            "no_labels_food_products",
        ],
        "specific_print",
        "alc_label_printing_base",
    )

    openupgrade.update_module_moved_models(
        env.cr,
        "print.label",
        "specific_print",
        "alc_label_printing_base",
    )
    openupgrade.update_module_moved_fields(
        env.cr,
        "print.label",
        [
            "label_type",
            "printer_id",
            "picking_ids",
            "qty",
        ],
        "specific_print",
        "alc_label_printing_base",
    )

    openupgrade.update_module_moved_fields(
        env.cr,
        "print.label",
        [
            "lot_ids",
            "move_line_ids",
        ],
        "specific_print",
        "alc_product_label_printing",
    )

    openupgrade.update_module_moved_fields(
        env.cr,
        "stock.picking",
        [
            "checksum",
            "printed_once",
        ],
        "specific_print",
        "alc_label_printing_base",
    )

    openupgrade.rename_xmlids(
        env.cr,
        [
            (
                "specific_print.report_stock_pick_packs_label",
                "alc_label_printing_base.report_stock_pick_packs_label",
            ),
            (
                "specific_print.report_stock_product_label",
                "alc_product_label_printing.report_stock_product_label",
            ),
            (
                "specific_print.report_lot_label",
                "alc_product_label_printing.report_lot_label",
            ),
            (
                "specific_print.report_lot_nolot_label",
                "alc_product_label_printing.report_lot_nolot_label",
            ),
            (
                "specific_print.report_stock_product_food_label",
                "alc_product_label_printing.report_stock_product_food_label",
            ),
        ],
    )
