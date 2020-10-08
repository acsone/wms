# -*- coding: utf-8 -*-
# Copyright 2018 Sylvain Van Hoof (Okia SPRL)
# Copyright 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import odoo.addons.decimal_precision as dp
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class ReceptionPharmacy(models.Model):
    _name = "reception.pharmacy"
    _rec_name = "date"

    date = fields.Datetime(default=lambda self: fields.Datetime.now(), copy=False)
    product_id = fields.Many2one(
        "product.product",
        string="Product",
        default=lambda self: self.env.ref("specific_stock.product_colis_souverain"),
        required=True,
        domain=lambda s: s._domain_product_id(),
    )
    line_ids = fields.One2many(
        "reception.pharmacy.line",
        "wizard_id",
        string="Lines",
        states={"done": [("readonly", True)]},
    )
    state = fields.Selection(
        [("draft", "New"), ("done", "Done")], copy=False, readonly=True, default="draft"
    )

    @api.model
    def _domain_product_id(self):
        return [
            (
                "id",
                "in",
                [
                    self.env.ref("specific_stock.product_colis_souverain").id,
                    self.env.ref("specific_stock.product_colis_souverain_frigo").id,
                ],
            )
        ]

    def validate(self):
        self.ensure_one()

        if not self.line_ids:
            raise UserError(_("Please insert at least one line"))

        proc_group = self.env["procurement.group"]
        proc_order = self.env["procurement.order"]
        lot = self.env["stock.production.lot"]
        move = self.env["stock.move"]
        sequence = self.env["ir.sequence"]

        warehouse = self.env.ref("stock.warehouse0")
        if not warehouse:
            raise UserError(_("Warehouse is missing"))
        loc_customer = self.env.ref("stock.stock_location_customers")
        if not loc_customer:
            raise UserError(_("Customer location is missing"))
        loc_supplier = self.env.ref("stock.stock_location_suppliers")
        if not loc_supplier:
            raise UserError(_("Supplier location is missing"))

        for partner in self.line_ids.mapped("customer_id"):
            if not partner.round_itinerary_ids:
                raise UserError(
                    _("Partner {} does not belong to any itinerary").format(
                        partner.name
                    )
                )

        for line in self.line_ids:
            lot_id = lot.create(
                {
                    "product_id": self.product_id.id,
                    "name": sequence.next_by_code("stock.lot.pharmacy"),
                    "voice_identifier": "ABC",
                    "checksum": "123",
                }
            )
            # Put the lot in stock
            line.reception_move_id = move.create(
                {
                    "name": "Pharmacy",
                    "product_id": self.product_id.id,
                    "product_uom": self.product_id.uom_id.id,
                    "restrict_lot_id": lot_id.id,
                    "product_uom_qty": line.product_qty,
                    "location_id": loc_supplier.id,
                    "location_dest_id": line.bin_id.id,
                }
            )
            line.reception_move_id.action_done()
            # Plan a delivery
            # The procurement will create the ship and pick
            group_id = proc_group.create(
                {
                    "partner_id": line.partner_shipping_id.id,
                    "customer_id": line.customer_id.id,
                }
            )
            line.procurement_id = proc_order.create(
                {
                    "name": "Pharmacy",
                    "product_id": self.product_id.id,
                    "product_uom": self.product_id.uom_id.id,
                    "restrict_lot_id": lot_id.id,
                    "product_qty": line.product_qty,
                    "warehouse_id": warehouse.id,
                    "location_id": loc_customer.id,
                    "partner_dest_id": line.customer_id.id,
                    "group_id": group_id.id,
                }
            )
            line.procurement_id.run()
            pickings = (
                self.env["stock.move"]
                .search([("group_id", "=", group_id.id)])
                .mapped("picking_id")
            )
            pickings = pickings.filtered(
                lambda picking: picking.picking_type_subcode == "PICK"
                and picking.state not in ("draft", "done", "cancel")
                and not picking.printed
            )
            delivery_round = pickings.mapped("delivery_round_id")
            if len(delivery_round) > 1:
                raise ValidationError(
                    _(
                        "All pickings at destination of a same shipping must "
                        "be in the same delivery round"
                    )
                )
            if not delivery_round:
                delivery_round = self.env["round.instance"].find_bypartner(
                    pickings[0].partner_id
                )
            if delivery_round:
                delivery_round._assign_pickings(pickings)
        self.state = "done"


class ReceptionPharmacyLine(models.Model):
    _name = "reception.pharmacy.line"
    _rec_name = "wizard_id"

    wizard_id = fields.Many2one("reception.pharmacy", required=True, string="Wizard")
    customer_id = fields.Many2one(
        "res.partner", string="Customer", required=True, ondelete="restrict"
    )
    bin_id = fields.Many2one(
        "stock.location",
        domain=[("usage", "=", "internal"), ("act_as_view", "=", False)],
        string="Bin",
        required=True,
        ondelete="restrict",
    )
    product_qty = fields.Float(
        "Quantity",
        digits=dp.get_precision("Product Unit of Measure"),
        default=1.0,
        required=True,
    )
    reception_move_id = fields.Many2one(
        "stock.move", string="Reception Move", readonly=True
    )
    procurement_id = fields.Many2one(
        "procurement.order", string="Delivery Procurement", readonly=True
    )

    partner_shipping_id = fields.Many2one(
        "res.partner", string="Delivery Address", compute="_compute_partner_shipping_id"
    )

    @api.multi
    def _compute_partner_shipping_id(self):
        """
        Trigger the change of the shipping address if the customer is modified.
        """
        for rec in self:
            if rec.customer_id:
                address = rec.customer_id.address_get(["delivery", "invoice"])
                rec.partner_shipping_id = address["delivery"]
