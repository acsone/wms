# Copyright 2019 Camptocamp SA
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, fields

from odoo.addons.base_exception.models.exception_rule import ExceptionRule
from odoo.addons.sale_exception.models import sale_order_line


class SaleOrderLine(sale_order_line.SaleOrderLine):
    main_exception_id = fields.Many2one[ExceptionRule](
        compute="_compute_main_exception_id",
        string="Main Exception",
        store=True,
    )
    exception_ids = fields.Many2many[ExceptionRule](
        compute="_compute_exception_ids", readonly=False, precompute=True, store=True
    )
    warning_text = fields.Char(compute="_compute_warning_text")

    @api.depends("exception_ids", "ignore_exception")
    def _compute_main_exception_id(self):
        for line in self:
            if not line.ignore_exception and line.exception_ids:
                # ensure the exception_ids are sorted by sequence. It's required
                # since the recordset could come from cache and be unordered
                line.main_exception_id = line.exception_ids.sorted("sequence")[0]
            else:
                line.main_exception_id = False

    @api.depends("product_id", "order_id.partner_id", "price_subtotal")
    def _compute_exception_ids(self):
        __all_exception_ids, rules_to_remove, rules_to_add = self._get_exceptions()
        for rule_id, records in rules_to_remove.items():
            records.exception_ids = [(3, rule_id)]
        for rule_id, records in rules_to_add.items():
            records.exception_ids = [(4, rule_id)]

    @api.depends("exception_ids")
    def _compute_warning_text(self):
        for line in self:
            # remove False or empty strings and remove blocking exceptions -> warnings only
            descriptions = [
                e.description
                for e in line.exception_ids.sorted("sequence")
                if e.description and not e.is_blocking
            ]
            line.warning_text = "\n".join(descriptions)

    @api.depends("exception_ids", "warning_text")
    def _compute_name(self):
        res = super()._compute_name()
        for line in self:
            if line.warning_text:
                line.name = (
                    (line.name or line.product_id.display_name or "")
                    + "\n"
                    + line.warning_text
                )
        return res
