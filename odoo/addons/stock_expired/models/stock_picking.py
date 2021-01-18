# -*- coding: utf-8 -*-
# Copyright 2016 Julien Coux (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import date

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT

DATE_LENGTH = len(date.today().strftime(DATE_FORMAT))


class StockPicking(models.Model):
    _inherit = "stock.picking"

    to_process_quant_expired = fields.Boolean("Bypass restriction on expired quants")

    @api.multi
    def check_expired_lot_on_transfer(self):

        for picking in self:
            bad_lots = []
            stock_op_lots = picking.pack_operation_ids.mapped("pack_lot_ids")
            for line in stock_op_lots:
                if line.is_product_expired and not picking.to_process_quant_expired:
                    bad_lots.append(
                        "%s (%s)"
                        % (line.lot_id.name, line.lot_id.expiry_date[:DATE_LENGTH])
                    )
            if bad_lots:
                raise UserError(
                    _(
                        "You cannot transfer lots with an expired "
                        "removal date:\n\t- %s"
                    )
                    % ("\n\t- ".join(bad_lots))
                )

    @api.multi
    def do_new_transfer(self):
        self.ensure_one()
        result = super(StockPicking, self).do_new_transfer()
        self.check_expired_lot_on_transfer()
        return result
