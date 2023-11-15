# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.addons.base.models.res_partner import Partner as PartnerBase


class ResPartner(PartnerBase):
    def action_view_sale_lines_unavailable(self):
        self.ensure_one()

        action_data = self.env.ref(
            "alc_sale_order_line_unavailable_list.action_sale_order_line_unavailable_list"
        ).read()[0]
        action_data["domain"] = [
            ("state", "in", ["sale", "done"]),
            ("order_id.partner_id", "=", self.id),
        ]

        return action_data
