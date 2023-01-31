# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields

from odoo.addons.sale.models import sale_order


class SaleOrder(sale_order.SaleOrder):

    suite_name = fields.Char(string="Suite Id", copy=False)

    def init(self):
        res = super().init()
        # This partial index is used by the 'last_suite_name' computed field
        # on 'res.partner' (use of 'LIMIT 1' making PostgreSQL slow under
        # certain circumstances).
        query = """
            CREATE INDEX IF NOT EXISTS
            sale_order_partner_id_date_order_id_partial_index
            ON sale_order (partner_id, date_order DESC, id DESC)
            WHERE suite_name IS NOT NULL;
        """
        self.env.cr.execute(query)
        return res

    @api.model
    def get_next_suite_name(self, cart):
        return cart.partner_id.with_prefetch(None).next_suite_name
