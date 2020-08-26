# -*- coding: utf-8 -*-
# © 2016 Julien Coux (Camptocamp)
# © 2017 Jacques-Etienne Baudoux (BCIM)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from datetime import datetime

from odoo import api, fields, models


class StockPackOperationLot(models.Model):
    _inherit = "stock.pack.operation.lot"

    life_date = fields.Datetime(string="Expiration date")
    is_removal_date_expired = fields.Boolean(
        "Removal date", compute="_get_is_removal_date_expired"
    )

    @api.depends("lot_id.life_date", "operation_id")
    @api.one
    def _get_is_removal_date_expired(self):
        # CODE TO BE MOVED
        # Thsi code should be put into a specific addon with the
        # method using it
        # see specific_stock/stock_picking/check_removal_date_on_transfer
        product = self.operation_id.product_id
        is_removal_date_expired = False
        if product and self.lot_id.life_date:
            if product.removal_time:
                lot = self.env["stock.production.lot"].new(
                    {"product_id": product.id, "life_date": self.lot_id.life_date}
                )
                lot.onchange_life_date()
                if (
                    lot.removal_date
                    and fields.Datetime.from_string(lot.removal_date) < datetime.now()
                ):
                    is_removal_date_expired = True
        self.is_removal_date_expired = is_removal_date_expired

    def _calc_lotname_from_lifedate(self, pack_op, life_date):
        """ The default lot name is only for an aliment """
        picking_zone = pack_op.product_id.picking_zone_id
        if picking_zone != self.env.ref("__setup__.picking_zone_aliments"):
            return

        date = fields.Datetime.from_string(life_date)
        date_with_timezone = fields.Datetime.context_timestamp(self, date)
        return date_with_timezone.strftime("%d%m%y")

    @api.onchange("life_date")
    def _onchange_life_date(self):
        if self.life_date and self.operation_id:
            self.lot_name = self._calc_lotname_from_lifedate(
                self.operation_id, self.life_date
            )

    @api.multi
    def write(self, vals):
        result = super(StockPackOperationLot, self).write(vals)
        if vals.get("lot_id"):
            for pack_operation_lot in self:
                life_date = pack_operation_lot.life_date
                if life_date:
                    pack_operation_lot.lot_id.life_date = life_date
                    pack_operation_lot.lot_id.onchange_life_date()
        return result

    @api.model
    def create(self, vals):
        if vals.get("lot_id") and not vals.get("life_date"):
            lot = self.env["stock.production.lot"].browse(vals["lot_id"])
            vals["life_date"] = lot.life_date
        return super(StockPackOperationLot, self).create(vals)
