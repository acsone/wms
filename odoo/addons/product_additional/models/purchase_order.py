# -*- coding: utf-8 -*-
# Copyright 2018 Sylvain Van Hoof (Okia SPRL)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.multi
    def button_compute_additional_products(self):
        """
        Compute additional products for a recordsets of purchae orders.
        In a first time, this method will delete all existing additional
        lines. After that, for each line, the method will check if we
        need to create an additional line.
        """
        # Remove existing additional lines. These lines will be
        # recomputed if needed
        existing_additional_lines = self.mapped("order_line").filtered(
            lambda line: line.is_additional_product
        )
        existing_additional_lines.unlink()

        for order in self:
            for line in order.order_line:
                ratio_main_product = line.product_id.ratio_main_product
                ratio_additional_product = line.product_id.ratio_additional_product
                additional_product_id = line.product_id.additional_product_id

                if (
                    not ratio_main_product
                    or not ratio_additional_product
                    or not additional_product_id
                ):
                    continue

                coefficient = int(line.product_qty / ratio_main_product)
                additional_product = coefficient * ratio_additional_product
                if not additional_product:
                    continue

                # Set the language of the supplier
                additional_product_lang = additional_product_id.with_context(
                    lang=order.partner_id.lang, partner_id=order.partner_id.id
                )

                line.copy(
                    default={
                        "name": additional_product_lang.display_name,
                        "order_id": order.id,
                        "price_unit_base": 0,
                        "price_unit": 0,
                        "product_id": additional_product_id.id,
                        "product_uom": line.product_uom.id,
                        "product_qty": additional_product,
                        "is_additional_product": True,
                    }
                )

    @api.multi
    def button_draft(self):
        """
        Remove additional product
        :return:
        """
        result = super(PurchaseOrder, self).button_draft()
        self._remove_additional_lines()
        return result

    @api.multi
    def _remove_additional_lines(self):
        lines_to_remove = self.mapped("order_line").filtered(
            lambda line: line.is_additional_product
        )
        lines_to_remove.unlink()

    @api.multi
    @api.returns(None, lambda value: value[0])
    def copy_data(self, default=None):
        res = super(PurchaseOrder, self).copy_data(default=default)
        # Skip additional lines on duplicate
        if "order_line" in res[0]:
            for i, line in reversed(list(enumerate(res[0]["order_line"]))):
                if line[0] == 0 and line[2].get("is_additional_product"):
                    del res[0]["order_line"][i]
        return res


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    is_additional_product = fields.Boolean("Additional product")
