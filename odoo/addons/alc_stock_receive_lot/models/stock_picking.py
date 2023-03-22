# © 2017 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.addons.stock.models.stock_picking import Picking as PickingBase


class Picking(PickingBase):
    def button_receive(self):
        self.ensure_one()

        if not self.user_id:
            self.user_id = self.env.user
            self.printed = True

        return self.env.ref(
            "alc_stock_receive_lot.action_pack_operation_lot_add"
        ).read()[0]
