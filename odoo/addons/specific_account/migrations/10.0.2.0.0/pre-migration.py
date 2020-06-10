# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def migrate(cr, version):
    # Move fields to alc_sale_invoicing_policy
    openupgrade.update_module_moved_fields(
        cr,
        "res.partner",
        ["invoice_frequency", "invoice_grouping"],
        "specific_account",
        "alc_sale_invoicing_policy",
    )

    openupgrade.update_module_moved_fields(
        cr,
        "sale.order",
        ["is_unique_invoice"],
        "specific_account",
        "alc_sale_invoicing_policy",
    )

    # Moved fields to alc_sale_invoicing_on_transfer

    openupgrade.update_module_moved_fields(
        cr,
        "stock.picking.type",
        ["create_invoice_on_transfer"],
        "specific_account",
        "alc_sale_invoicing_on_transfer",
    )

    # Moved xml_id to alc_sale_invoicing_policy
    openupgrade.rename_xmlids(
        cr,
        [
            (
                "specific_account.ir_cron_invoice_10",
                "alc_sale_invoicing_policy.ir_cron_invoice_10",
            ),
            (
                "specific_account.ir_cron_invoice_20",
                "alc_sale_invoicing_policy.ir_cron_invoice_20",
            ),
            (
                "specific_account.ir_cron_invoice_31",
                "alc_sale_invoicing_policy.ir_cron_invoice_31",
            ),
        ],
    )

    # remove views moved to alc_sale_invoicing_policy
    cr.execute(
        """
    delete from ir_ui_view where id in (
        select
            res_id
        from
            ir_model_data
        where
            module='specific_account'
            and model='ir.ui.view'
            and name='view_partner_property_form'
    );
    delete from ir_ui_view where id in (
        select
            res_id
        from
            ir_model_data
        where
            module='specific_account'
            and model='ir.ui.view'
            and name='view_order_form'
    );
    """
    )
    # remove views moved to alc_sale_invoicing_on_transfer
    cr.execute(
        """
       delete from ir_ui_view where id in (
           select
               res_id
           from
               ir_model_data
           where
               module='specific_account'
               and model='ir.ui.view'
               and name='view_picking_type_form'
       );
       """
    )
