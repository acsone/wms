# © 2017 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields

from odoo.addons.sale_stock.models.sale_order_line import (
    SaleOrderLine as SaleOrderLineBase,
)


class SaleOrderLine(SaleOrderLineBase):

    is_consignment = fields.Boolean(
        related="order_id.is_consignment", readonly=True, store=True
    )

    def _get_partner_consignment_location_values(self):
        consignment_location = self.env.ref(
            "alc_sale_consignment.stock_location_consignment"
        )
        return {
            "location_id": consignment_location.id,
            "name": self.order_id.partner_shipping_id.display_name,
            "usage": "internal",
            "company_id": self.order_id.company_id.id,
        }

    def _get_partner_consignment_location(self):
        self.ensure_one()
        partner = self.order_id.partner_shipping_id
        location = partner.property_stock_consignment_customer
        if location:
            return location
        # user may not have 'create' access for stock location
        location_model_sudo = self.env["stock.location"].sudo()
        location = location_model_sudo.create(
            self._get_partner_consignment_location_values()
        )
        partner.sudo().property_stock_consignment_customer = location
        return location

    def _prepare_procurement_values(self, group_id=False):
        values = super()._prepare_procurement_values(group_id)
        if not self.is_consignment:
            return values
        values["location_id"] = self._get_partner_consignment_location()
        return values

    @api.depends(
        "move_ids.state",
        "move_ids.scrapped",
        "move_ids.product_uom_qty",
        "move_ids.product_uom",
        "is_consignment",
    )
    def _compute_qty_delivered(self):
        """Consignment deliveries are not billable, so we disable quantity tracking.

        in sale order
        """
        res = super()._compute_qty_delivered()
        for rec in self:
            if rec.is_consignment:
                rec.qty_delivered = 0
        return res
