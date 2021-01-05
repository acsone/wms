# -*- coding: utf-8 -*-
# © 2016 Julien Coux (Camptocamp)
# © 2017 Jacques-Etienne Baudoux (BCIM)
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class StockPackOperationLot(models.Model):
    _inherit = "stock.pack.operation.lot"

    life_date = fields.Datetime(string="Expiration date")

    is_product_expired = fields.Boolean(related="lot_id.is_expired", readonly=True)

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
