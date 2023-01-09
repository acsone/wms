# -*- coding: utf-8 -*-
# Copyright 2018 Sylvain Van Hoof (Okia SPRL)
# Copyright 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

import odoo.addons.decimal_precision as dp
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

    @api.constrains("customer_id")
    def _check_customer_id(self):
        for rec in self:
            if not rec.customer_id.is_delivered_by_alcyon:
                raise ValidationError(
                    _("Partner {} does not belong to any itinerary").format(
                        rec.partner_shipping_id.name
                    )
                )

    def print_reception_pharmacy_label(self, printer=False):
        self.ensure_one()
        if not printer:
            printer = self.env.user.printing_pharmacy_reception_printer_id
        hw_print(
            self,
            "alc_reception_pharmacy.report_pharmacy_lot_label",
            qty=1,
            printer_id=printer.id,
        )
