# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models

QUICK_EDIT_MODE = "force_quick_edit"


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    is_quick_edited = fields.Boolean()

    @api.model
    def _is_in_quick_edit_mode(self):
        return self.env.context.get(QUICK_EDIT_MODE, False)

    @api.depends('carrier_id', 'order_line')
    def _compute_delivery_price(self):
        if self._is_in_quick_edit_mode():
            return
        return super(SaleOrder, self)._compute_delivery_price()

    @api.depends('order_line.price_total')
    def _amount_all(self):
        if self._is_in_quick_edit_mode():
            return
        return super(SaleOrder, self)._amount_all()

    @api.depends('state', 'order_line.invoice_status')
    def _get_invoiced(self):
        if self._is_in_quick_edit_mode():
            return
        return super(SaleOrder, self)._get_invoiced()

    def action_confirm_background(self):
        self._finalize_quick_edit()
        return super(SaleOrder, self).action_confirm_background()

    def action_confirm(self):
        self._finalize_quick_edit()
        return super(SaleOrder, self).action_confirm()

    @api.multi
    def _finalize_quick_edit(self):
        for record in self:
            if not self.is_quick_edited:
                continue
            record._compute_delivery_price()
            record._amount_all()
            record._get_invoiced()
            record.write({"is_quick_edited": False})

    @api.multi
    def action_finalize_quick_edit(self):
        self._finalize_quick_edit()

    @api.multi
    def action_open_line_fast_entry(self):
        """
        Launch the editable tree view for the current sale order to allow
        fast line creation.
        When a line is created into the fast line creation screen, some computed
        methods on the SO are disabled to speedup the line creation. Therefore
        we mark the SO as to be recalculated before validation.
        We also activate the readonly bypass for product_qty_unavailable, to avoid
        the recompute of this field at save time which has already been computed
        by the onchange to be displayed on the screen
        :return:
        """
        self.ensure_one()
        self.write({"is_quick_edited": True})
        return {
            "name": _("Sale Order Lines"),
            "type": "ir.actions.act_window",
            "view_mode": "tree",
            "res_model": "sale.order.line",
            "view_id": self.env.ref(
                "sale_quick_create.sale_order_line_tree_edit"
            ).id,
            "search_view_id": self.env.ref(
                "sale.view_sales_order_line_filter"
            ).id,
            "domain": [('order_id', '=', self.id)],
            "context": {
                'default_order_id': self.id,
                "readonly_by_pass": ['product_qty_unavailable'],
                QUICK_EDIT_MODE: True,
            },
        }
