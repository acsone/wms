# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, tools


class AlcStockMoveReport(models.Model):

    _name = "alc.stock.move.report"
    _description = "Stock move report"
    _auto = False
    _order = "validation_date desc"

    customer_in_statistics = fields.Boolean("Customer in statistics", readonly=True)

    internal_ref_for_partner_invoice = fields.Char(
        "Internal Ref for invoicing", readonly=True
    )

    location_dest_id = fields.Many2one(
        "stock.location",
        "Destination Location",
        auto_join=True,
        index=True,
        required=True,
        states={"done": [("readonly", True)]},
        help="Location where the system will stock the finished products.",
    )
    location_id = fields.Many2one(
        "stock.location",
        "Source Location",
        auto_join=True,
        index=True,
        required=True,
        states={"done": [("readonly", True)]},
        help="Sets a location if you produce at a fixed location. This can be a partner location if you subcontract the manufacturing operations.",
    )

    partner_invoice_alcyon_category = fields.Char(
        "Partner Alcyon category for invoicing", readonly=True
    )
    partner_invoice_city = fields.Char("Partner city for invoicing", readonly=True)
    partner_invoice_depot_number = fields.Char(
        "Partner depot numbr for invoicing", readonly=True
    )
    partner_invoice_name = fields.Char("Partner name for invoicing", readonly=True)
    partner_invoice_street = fields.Char("Partner street for invoicing", readonly=True)
    partner_invoice_vat = fields.Char("Partner vat for invoicing", readonly=True)
    partner_invoice_zip = fields.Char("Partner zip for invoicing", readonly=True)

    picking_reference = fields.Char("Picking reference", readonly=True)

    price_unit = fields.Float(string="Unit Price", readonly=True)

    product_id = fields.Many2one("product.product", "Product", readonly=True)
    product_default_code = fields.Char("Product default code")
    product_name = fields.Char("Name", index=True, required=True, translate=True)
    product_price = fields.Float("Sale Price", default=1.0, readonly=True)
    product_qty = fields.Float("Product quantity", required=True, readonly=True)
    product_sale_price_2 = fields.Float(
        related="product_id.product_tmpl_id.sale_price_2", readonly=True
    )
    product_standard_price = fields.Float(
        related="product_id.standard_price", readonly=True
    )

    state = fields.Selection(
        [
            ("draft", "New"),
            ("cancel", "Cancelled"),
            ("waiting", "Waiting Another Move"),
            ("confirmed", "Waiting Availability"),
            ("assigned", "Available"),
            ("done", "Done"),
        ],
        string="Status",
        copy=False,
        default="draft",
        index=True,
        readonly=True,
        help="* New: When the stock move is created and not yet confirmed.\n"
        "* Waiting Another Move: This state can be seen when a move is waiting for another one, for example in a chained flow.\n"
        "* Waiting Availability: This state is reached when the procurement resolution is not straight forward. It may need the scheduler to run, a component to be manufactured...\n"
        "* Available: When products are reserved, it is set to 'Available'.\n"
        "* Done: When the shipment is processed, the state is 'Done'.",
    )

    supplier_ref = fields.Char("Vendor Product Code", readonly=True)
    supplier_name = fields.Char("Vendor Product Name", readonly=True)
    validation_date = fields.Date("Validation date", readonly=True)

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, "alc_stock_move_report")
        self._cr.execute(
            """
            create view alc_stock_move_report as (
                SELECT sm.id AS id,
                       sm.product_id AS product_id,
                       sm.state AS state,
                       sm.location_id AS location_id,
                       sm.location_dest_id AS location_dest_id,
                       sm.validation_date AS validation_date,
                       sm.product_uom_qty AS product_qty,
                       pt.default_code AS product_default_code,
                       pt.name AS product_name,
                       pt.list_price AS product_price,
                       pt.vendor_product_code AS supplier_ref,
                       sol.price_unit AS price_unit,
                       resp.ref AS internal_ref_for_partner_invoice,
                       resp.name AS partner_invoice_name,
                       resp.street AS partner_invoice_street,
                       resp.city AS partner_invoice_city,
                       resp.zip AS partner_invoice_zip,
                       resp.vat AS partner_invoice_vat,
                       resp.vet_depot_number AS partner_invoice_depot_number,
                       resp.alcyon_category_id AS partner_invoice_alcyon_category,
                       resp.is_in_statistics AS customer_in_statistics,
                       pick.name AS picking_reference,
                       suppl.name AS supplier_name
                FROM stock_move sm
                    JOIN product_product pp ON pp.id = sm.product_id
                    JOIN product_template pt ON pt.id = pp.product_tmpl_id
                    JOIN sale_order_line sol ON sol.id = sm.order_line_id
                    JOIN sale_order so ON so.id = sol.order_id
                    JOIN res_partner resp ON resp.id = so.partner_invoice_id
                    JOIN stock_picking pick ON pick.id = sm.picking_id
                    JOIN res_partner suppl ON suppl.id = pt.supplier_id
            )
        """
        )
