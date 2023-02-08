# -*- coding: utf-8 -*-
# Copyright 2018 Sylvain Van Hoof (Okia SPRL)
# Copyright 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

import odoo.addons.decimal_precision as dp
from odoo.addons.queue_job.job import job, related_action
from odoo.addons.specific_print.utils import hw_print


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
        "res.partner",
        string="Delivery Address",
        related="customer_id.partner_shipping_id",
        readonly=True,
    )
    lot_id = fields.Many2one("stock.production.lot", "Lot")
    product_id = fields.Many2one(
        "product.product",
        string="Product",
        related="wizard_id.product_id",
        readonly=True,
    )
    state = fields.Selection(
        [("draft", "New"), ("done", "Done")], copy=False, readonly=True, default="draft"
    )

    @api.constrains("customer_id")
    def _check_customer_id(self):
        for rec in self:
            if not rec.customer_id.is_delivered_by_alcyon:
                raise ValidationError(
                    _("Partner {} does not belong to any itinerary").format(
                        rec.partner_shipping_id.name
                    )
                )

    def print_reception_pharmacy_label(self):
        self.ensure_one()
        printer = self.env.user.printing_pharmacy_reception_printer_id
        if not printer:
            raise ValidationError(
                _("No printer defined for reception, please select one first")
            )
        hw_print(
            self,
            "alc_reception_pharmacy.report_pharmacy_lot_label",
            qty=1,
            printer_id=printer.id,
        )

    @job(default_channel="root.background.process")
    @related_action(action="related_action_open_reception_pharmacy")
    def validate(self):
        proc_group = self.env["procurement.group"]
        proc_order = self.env["procurement.order"]
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
                    "location_id": loc_supplier.id,
                    "location_dest_id": rec.bin_id.id,
                }
            )
            rec.reception_move_id.action_done()
            # Plan a delivery
            # The procurement will create the ship and pick
            group_id = proc_group.create(
                {
                    "partner_id": rec.partner_shipping_id.id,
                    "customer_id": rec.customer_id.id,
                    "carrier_id": carrier.id,
                }
            )
            proc_order_vals = self._prepare_procurement_order(
                rec, rec.lot_id.id, warehouse.id, loc_customer.id, group_id.id
            )
            rec.procurement_id = proc_order.create(proc_order_vals)
            # procurement_autorun_defer
            rec.procurement_id.run()
            pickings = move.search([("group_id", "=", group_id.id)]).mapped(
                "picking_id"
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
                description = (
                    _("Assign pickings to delivery round %s after pharmacy reception.")
                    % delivery_round.display_name
                )
                delivery_round.with_delay(
                    description=description, priority=8
                )._assign_pickings(pickings)
            rec.state = "done"

    def _prepare_procurement_order(
        self, line, lot_id, warehouse_id, loc_customer_id, group_id
    ):
        proc_order = self.env["procurement.order"]
        proc_order_vals = {
            "name": "Pharmacy",
            "product_id": self.product_id.id,
            "product_uom": self.product_id.uom_id.id,
            "product_qty": line.product_qty,
            "warehouse_id": warehouse_id,
            "location_id": loc_customer_id,
            "partner_dest_id": line.customer_id.id,
            "group_id": group_id,
            "delivery_requires_other_lines": True,
        }
        # HACK HACK HACK for fields declared in specific_Stock.... TO BE
        # REFACTORED!!!!!!
        if "restrict_lot_id" in proc_order._fields:
            proc_order_vals["restrict_lot_id"] = lot_id
        return proc_order_vals
