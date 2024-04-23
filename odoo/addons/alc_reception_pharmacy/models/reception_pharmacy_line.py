# Copyright 2018 Sylvain Van Hoof (Okia SPRL)
# Copyright 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

from odoo.addons.product.models.product_product import ProductProduct
from odoo.addons.stock.models.stock_location import Location
from odoo.addons.stock.models.stock_lot import StockLot
from odoo.addons.stock.models.stock_move import StockMove

from .res_partner import ResPartner


class ReceptionPharmacyLine(models.Model):
    _name = "reception.pharmacy.line"
    _rec_name = "wizard_id"
    _description = "Line of reception pharmacy"

    wizard_id = fields.Many2one["ReceptionPharmacy"](required=True, string="Wizard")
    customer_id = fields.Many2one[ResPartner](
        string="Customer", required=True, ondelete="restrict"
    )
    bin_id = fields.Many2one[Location](
        domain=[("usage", "=", "internal")],
        string="Bin",
        required=True,
        ondelete="restrict",
    )
    product_qty = fields.Float(
        "Quantity",
        digits="Product Unit of Measure",
        default=1.0,
        required=True,
    )
    reception_move_id = fields.Many2one[StockMove](
        string="Reception Move", readonly=True, index=True
    )
    partner_shipping_id = fields.Many2one[ResPartner](
        string="Delivery Address",
        related="customer_id.partner_shipping_id",
        readonly=True,
    )
    lot_id = fields.Many2one[StockLot](string="Lot")
    product_id = fields.Many2one[ProductProduct](
        string="Product",
        related="wizard_id.product_id",
        readonly=True,
    )
    state = fields.Selection(
        [("draft", "New"), ("done", "Done")], copy=False, readonly=True, default="draft"
    )

    @api.constrains("customer_id")
    def _check_customer_id(self):
        if self.env.user.company_id.delivered_by_alcyon_constraint:
            for rec in self:
                if not rec.customer_id.is_delivered_by_alcyon:
                    raise ValidationError(
                        _(
                            "Partner %(partner)s does not belong to any release "
                            "channel",
                            partner=rec.partner_shipping_id.name,
                        )
                    )

    def validate(self):
        proc_group = self.env["procurement.group"]
        move = self.env["stock.move"]
        warehouse = self.env.ref("stock.warehouse0")
        carrier = self.env.ref("__setup__.deliver_carrier_alcyon")
        if not warehouse:
            raise UserError(_("Warehouse is missing"))
        loc_customer = self.env.ref("stock.stock_location_customers")
        if not loc_customer:
            raise UserError(_("Customer location is missing"))
        loc_supplier = self.env.ref("stock.stock_location_suppliers")
        if not loc_supplier:
            raise UserError(_("Supplier location is missing"))
        for rec in self:
            if rec.state != "draft":
                continue
            # Put the lot in stock
            rec.reception_move_id = move.create(
                {
                    "name": "Pharmacy",
                    "product_id": rec.product_id.id,
                    "product_uom": rec.product_id.uom_id.id,
                    "restrict_lot_id": rec.lot_id.id,
                    "product_uom_qty": rec.product_qty,
                    "quantity_done": rec.product_qty,
                    "location_id": loc_supplier.id,
                    "location_dest_id": rec.bin_id.id,
                }
            )
            rec.reception_move_id._action_done()
            # Plan a delivery
            # The procurement will create the ship and pick
            group_id = proc_group.create(
                {
                    "partner_id": rec.partner_shipping_id.id,
                    "customer_id": rec.customer_id.id,
                    "carrier_id": carrier.id,
                }
            )
            procurement = self._prepare_procurement(
                rec, loc_customer, warehouse, group_id
            )
            # procurement_autorun_defer
            group_id.run([procurement])
            rec.state = "done"

    def _prepare_procurement(self, line, loc_customer_id, warehouse_id, group_id):
        procurement = self.env["procurement.group"].Procurement
        return procurement(
            product_id=line.product_id,
            product_qty=line.product_qty,
            product_uom=line.product_id.uom_id,
            location_id=loc_customer_id,
            name="Pharmacy",
            origin="",
            company_id=self.env.user.company_id,
            values={
                "warehouse_id": warehouse_id,
                "group_id": group_id,
                "restrict_lot_id": line.lot_id.id,
            },
        )
