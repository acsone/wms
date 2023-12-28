# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import datetime

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from odoo.addons.base.models.res_partner import Partner
from odoo.addons.stock.models.stock_location import Location

from ..models.reception_pharmacy import ReceptionPharmacy


class ReceivePharmacyProducts(models.TransientModel):

    _name = "receive.pharmacy.products"
    _description = "Wizard of pharmacy reception"

    name = fields.Char(default="New")
    reception_pharmacy_id = fields.Many2one[ReceptionPharmacy](required=True)
    customer_id = fields.Many2one[Partner](string="Customer", ondelete="restrict")
    bin_id = fields.Many2one[Location](
        domain=[("usage", "=", "internal")],
        string="Bin",
        ondelete="restrict",
    )
    product_qty = fields.Float(
        "Quantity",
        digits="Product Unit of Measure",
        default=1.0,
    )
    lot_name = fields.Char(string="Lot")
    state = fields.Selection(related="reception_pharmacy_id.state")

    @api.onchange("customer_id")
    def _onchange_customer_id(self):
        self.bin_id = False
        self.lot_name = ""
        self.product_qty = 1

    def _check_reception_state(self):
        if self.reception_pharmacy_id.state == "done":
            raise ValidationError(
                _(
                    "This reception is transferred, please create a new one before "
                    "adding products to receive."
                )
            )

    def validate_reception(self):
        self._check_reception_state()
        self._add()
        action = self.env["ir.actions.actions"]._for_xml_id(
            "alc_reception_pharmacy.receive_pharmacy_products_act_window"
        )
        action["context"] = {
            "default_reception_pharmacy_id": self.reception_pharmacy_id.id
        }
        return action

    def _add(self):
        return self._create_reception_pharmacy_line()

    def _create_reception_pharmacy_line(self):
        product = self.reception_pharmacy_id.product_id
        reception_pharmacy_line = self.env["reception.pharmacy.line"]
        lot = self._create_lot(product)
        return reception_pharmacy_line.create(
            {
                "wizard_id": self.reception_pharmacy_id.id,
                "bin_id": self.bin_id.id,
                "customer_id": self.customer_id.id,
                "product_qty": self.product_qty,
                "partner_shipping_id": self.customer_id.partner_shipping_id.id,
                "lot_id": lot.id,
            }
        )

    def _create_lot(self, product):
        current_year = datetime.now().year
        lot_name = f"{current_year}{self.lot_name}"
        lot = self.env["stock.lot"]
        lot_vals = {
            "product_id": product.id,
            "name": lot_name,
            "company_id": self.env.user.company_id.id,
        }
        lot_id = lot.with_context(default_expiration_date_allowed=True).create(lot_vals)
        return lot_id
