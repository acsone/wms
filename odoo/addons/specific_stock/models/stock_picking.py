# -*- coding: utf-8 -*-
# Copyright 2016 Julien Coux (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    @api.multi
    def name_get(self):
        """ Display 'Warehouse code: PickingType_name' """
        res = []
        for picking_type in self:
            if picking_type.warehouse_id:
                name = u"{}: {}".format(
                    picking_type.warehouse_id.code, picking_type.name
                )
            else:
                name = picking_type.name
            res.append((picking_type.id, name))
        return res


class StockPicking(models.Model):
    _inherit = "stock.picking"

    is_put_in_pack_done = fields.Boolean("Put in Pack done", default=False)

    @api.multi
    def name_get(self):
        """ Display the name, the partner and the round """
        res = []
        for picking in self:
            name = picking.name
            if picking.partner_id:
                name += u" - %s" % picking.partner_id.display_name
            if picking.delivery_round_id:
                name += u" - %s" % picking.delivery_round_id.template_code
            res.append((picking.id, name))
        return res

    @api.multi
    def _create_lots_for_picking(self):
        return super(
            StockPicking, self.with_context(default_life_date_allowed=True)
        )._create_lots_for_picking()

    @api.multi
    def button_put_in_pack(self):
        self.ensure_one()
        pick = self
        operations_total = sum(
            x.qty_done
            for x in pick.pack_operation_ids
            if x.qty_done > 0 and (not x.result_package_id)
        )

        # A picking must be "put in pack" to be validated
        self.write({"is_put_in_pack_done": True})

        if not operations_total:
            return None

        wizard = self.env.ref("specific_stock.put_in_pack_helper_action")
        wizard_values = wizard.read()[0]

        # If the user pick in the aliment, we need to set the number of
        # packages to the picked qty. Other the number of packages equals 0
        pick_ali = self.env.ref("__setup__.stock_picking_type_ali")
        wizard_context = safe_eval(wizard_values.get("context", "{}"))
        if pick.picking_type_id == pick_ali:
            wizard_context["default_nbr_packages"] = int(operations_total)
        wizard_values["context"] = wizard_context

        return wizard_values
