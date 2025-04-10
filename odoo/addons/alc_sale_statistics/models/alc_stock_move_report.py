# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, tools

from odoo.addons.base.models.res_partner import Partner
from odoo.addons.product.models.product_product import ProductProduct
from odoo.addons.stock.models.stock_location import Location
from odoo.addons.stock.models.stock_move import StockMove


class AlcStockMoveReport(models.Model):

    _name = "alc.stock.move.report"
    _description = "Stock move report"
    _auto = False
    _order = "validation_date desc"

    move_id = fields.Many2one[StockMove](string="Stock move", readonly=True)
    supplier_ask_sale_statistics = fields.Boolean(
        "Supplier ask statistics", readonly=True
    )

    internal_ref_for_partner_invoice = fields.Char(
        "Internal Ref for invoicing", readonly=True
    )

    location_dest_id = fields.Many2one[Location](
        string="Destination Location", readonly=True
    )
    location_id = fields.Many2one[Location](string="Source Location", readonly=True)

    partner_id = fields.Many2one[Partner](string="Partner", readonly=True)
    partner_invoice_alcyon_category = fields.Char(
        "Partner Alcyon category for invoicing", readonly=True
    )
    partner_invoice_city = fields.Char("Partner city for invoicing", readonly=True)
    partner_invoice_depot_number = fields.Char(
        "Partner depot number for invoicing", readonly=True
    )
    partner_invoice_name = fields.Char("Partner name for invoicing", readonly=True)
    partner_invoice_street = fields.Char("Partner street for invoicing", readonly=True)
    partner_invoice_vat = fields.Char("Partner vat for invoicing", readonly=True)
    partner_invoice_zip = fields.Char("Partner zip for invoicing", readonly=True)
    partner_invoice_zip_prov = fields.Char(
        "Province partner zip for invoicing",
        compute="_compute_partner_invoice_zip_prov",
        readonly=True,
    )

    picking_reference = fields.Char("Picking reference", readonly=True)

    price_unit = fields.Float(string="Unit Price", readonly=True)

    product_id = fields.Many2one[ProductProduct](string="Product", readonly=True)
    product_default_code = fields.Char()
    product_name = fields.Char(readonly=True, translate=True)
    product_price = fields.Float(readonly=True)
    product_qty = fields.Integer("Product quantity", readonly=True)
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

    supplier_id = fields.Many2one[Partner](string="Supplier", readonly=True)
    supplier_ref = fields.Char("Vendor Product Code", readonly=True)
    supplier_name = fields.Char("Supplier name", readonly=True)
    validation_date = fields.Date("Validation date", readonly=True)
    sale_channel = fields.Char("Sale channel", readonly=True)

    def init(self):
        cr = self.env.cr
        tools.drop_view_if_exists(cr, "alc_stock_move_report")
        cr.execute(
            """
            create view alc_stock_move_report as (
                SELECT sm.id AS id,
                       sm.id AS move_id,
                       sm.product_id AS product_id,
                       sm.state AS state,
                       sm.location_id AS location_id,
                       sm.location_dest_id AS location_dest_id,
                       date(sm.date) AS validation_date,
                       CASE WHEN pick.name LIKE '%/IN/%' then -round(sm.product_uom_qty)::int else round(sm.product_uom_qty)::int end AS product_qty,
                       pt.default_code AS product_default_code,
                       pt.name AS product_name,
                       pt.list_price AS product_price,
                       pt.vendor_product_code AS supplier_ref,
                       sol.price_unit AS price_unit,
                       sol.sale_channel_id AS sale_channel,
                       resp.id as partner_id,
                       resp.ref AS internal_ref_for_partner_invoice,
                       resp.name AS partner_invoice_name,
                       resp.street AS partner_invoice_street,
                       resp.city AS partner_invoice_city,
                       resp.zip AS partner_invoice_zip,
                       resp.vat AS partner_invoice_vat,
                       resp.vet_depot_number AS partner_invoice_depot_number,
                       resp.partner_type AS partner_invoice_alcyon_category,
                       pick.name AS picking_reference,
                       suppl.id AS supplier_id,
                       suppl.name AS supplier_name,
                       suppl.ask_sale_statistics AS supplier_ask_sale_statistics
                FROM stock_move sm
                    JOIN product_product pp ON pp.id = sm.product_id
                    JOIN product_template pt ON pt.id = pp.product_tmpl_id
                    JOIN sale_order_line sol ON sol.id = sm.sale_line_id
                    JOIN sale_order so ON so.id = sol.order_id
                    JOIN res_partner resp ON resp.id = so.partner_invoice_id
                    JOIN stock_picking pick ON pick.id = sm.picking_id
                    JOIN res_partner suppl ON suppl.id = pt.supplier_id
            )
        """
        )

    def _compute_partner_invoice_zip_prov(self):  # noqa: C901
        """
        1000 - 2000 - 3000 - 4000 - 5000 - 6000 à 6599 (6000) - 6600 à 6999 (6600) -.

        7000 - 8000 - 9000
        """
        for rec in self:
            if rec.partner_invoice_zip < "2000":
                rec.partner_invoice_zip_prov = "1000"
            elif rec.partner_invoice_zip < "3000":
                rec.partner_invoice_zip_prov = "2000"
            elif rec.partner_invoice_zip < "4000":
                rec.partner_invoice_zip_prov = "3000"
            elif rec.partner_invoice_zip < "5000":
                rec.partner_invoice_zip_prov = "4000"
            elif rec.partner_invoice_zip < "6000":
                rec.partner_invoice_zip_prov = "5000"
            elif rec.partner_invoice_zip < "6600":
                rec.partner_invoice_zip_prov = "6000"
            elif rec.partner_invoice_zip < "7000":
                rec.partner_invoice_zip_prov = "6600"
            elif rec.partner_invoice_zip < "8000":
                rec.partner_invoice_zip_prov = "7000"
            elif rec.partner_invoice_zip < "9000":
                rec.partner_invoice_zip_prov = "8000"
            else:
                rec.partner_invoice_zip_prov = "9000"
