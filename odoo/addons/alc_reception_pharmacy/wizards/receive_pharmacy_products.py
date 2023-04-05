# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import datetime

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

import odoo.addons.decimal_precision as dp


class ReceivePharmacyProducts(models.TransientModel):

    _name = "receive.pharmacy.products"

    name = fields.Char(default="New")
    reception_pharmacy_id = fields.Many2one("reception.pharmacy", required=True)
    customer_id = fields.Many2one("res.partner", string="Customer", ondelete="restrict")
    bin_id = fields.Many2one(
        "stock.location",
        domain=[("usage", "=", "internal"), ("act_as_view", "=", False)],
        string="Bin",
        ondelete="restrict",
    )
    product_qty = fields.Float(
        "Quantity", digits=dp.get_precision("Product Unit of Measure"), default=1.0,
    )
    lot_name = fields.Char(string="Lot")
    state = fields.Selection(related="reception_pharmacy_id.state", default="draft")

    @api.model
    def default_get(self, fields_list):
        defaults = super(ReceivePharmacyProducts, self).default_get(fields_list)
        active_id = self._context.get("active_id", None)
        if active_id is None:
            return {}
        defaults["reception_pharmacy_id"] = active_id
        return defaults

    @api.onchange("customer_id")
    def _onchange_customer_id(self):
        self.bin_id = False
        self.lot_name = ""
        self.product_qty = 1

    def _check_reception_state(self):
        if self.reception_pharmacy_id.state == "done":
            raise ValidationError(
                _(
                    "This reception is transferred, please create a new one before adding products to receive."
                )
            )

    def validate_reception(self):
        self._check_reception_state()
        self._add()
        self._clean_wizard()

    def _add(self):
        reception_pharmacy_line = self._create_reception_pharmacy_line()
        self.print_reception_pharmacy_label(reception_pharmacy_line)

    def _create_reception_pharmacy_line(self):
        product = self.reception_pharmacy_id.product_id
        reception_pharmacy_line = self.env["reception.pharmacy.line"]
        lot = self._create_lot(product)
        line = reception_pharmacy_line.create(
            {
                "wizard_id": self.reception_pharmacy_id.id,
                "bin_id": self.bin_id.id,
                "customer_id": self.customer_id.id,
                "product_qty": self.product_qty,
                "partner_shipping_id": self.customer_id.partner_shipping_id.id,
                "lot_id": lot.id,
            }
        )
        return line

    def _create_lot(self, product):
        current_year = datetime.now().year
        lot_name = str(current_year) + self.lot_name
        lot = self.env["stock.production.lot"]
        lot_vals = {
            "product_id": product.id,
            "name": lot_name,
        }
        # HACK HACK HACK for fields declared in specific_Stock.... TO BE
        # REFACTORED!!!!!!
        if "voice_identifier" in lot._fields:
            lot_vals["voice_identifier"] = "ABC"
        if "checksum" in lot._fields:
            lot_vals["checksum"] = "123"
        # END HACK
        # TODO: ajouter datetime.now() dans les valeurs du create() pour life_date
        lot_id = lot.with_context(default_life_date_allowed=True).create(lot_vals)
        return lot_id

    def print_reception_pharmacy_label(self, reception_pharmacy_line):
        return reception_pharmacy_line.print_reception_pharmacy_label()

    def _clean_wizard(self):
        self.bin_id = False
        self.lot_name = ""
        self.product_qty = 1
        self.customer_id = False
