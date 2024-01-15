# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import models
from odoo.osv import expression


class MixinSaleLinesUnavailableAction(models.AbstractModel):
    _name = "mixin.sale.lines.unavailable.action"
    _description = "Provides the action that returns the related SO Lines"

    def _get_view_sale_lines_unavailable_record_id_domain(self):
        return []

    def _get_view_sale_lines_unavailable_sale_domain(self):
        self.ensure_one()
        return [("state", "in", ["sale", "done"])]

    def _get_view_sale_lines_unavailable_domain(self):
        self.ensure_one()
        return expression.AND(
            [
                self._get_view_sale_lines_unavailable_sale_domain(),
                self._get_view_sale_lines_unavailable_record_id_domain(),
            ]
        )

    def action_view_sale_lines_unavailable(self):
        self.ensure_one()

        action_data = self.env.ref(
            "alc_sale_order_line_unavailable_list.action_sale_order_line_unavailable_list"
        ).read()[0]
        action_data["domain"] = self._get_view_sale_lines_unavailable_domain()

        return action_data
