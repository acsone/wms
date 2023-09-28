# Copyright 2017-2018 Sylvain Van Hoof (Okia) <sylvain@okia.be>
# Copyright 2018 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import fields

from odoo.addons.stock.models.stock_move import StockMove as Move


class StockMove(Move):

    # This field is only used for information
    serial_number = fields.Char(
        "Serial number", readonly=True, help="For delivery order only"
    )
    show_serial_number = fields.Boolean(compute="_compute_show_serial_number")

    def _compute_show_serial_number(self):
        customer_location = self.env.ref("stock.stock_location_customers")
        for rec in self:
            rec.show_serial_number = rec.location_dest_id == customer_location

    def button_edit_serial_number(self):
        return self.env["ir.actions.act_window"]._for_xml_id(
            "alc_stock_move_serial_number.action_edit_serial_number"
        )
