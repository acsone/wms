# Copyright 2019 Camptocamp SA
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.addons.alc_sale_exception.models import sale_order_line


class SaleOrderLine(sale_order_line.SaleOrderLine):
    def warning_free_product(self):
        """Raise a warning if order give rights to promotional product."""
        return self.product_id.product_tmpl_id.get_promotional_product(
            self.product_uom_qty, self.product_id.uom_id, self.order_partner_id
        )
