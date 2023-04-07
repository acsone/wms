# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.purchase.models.res_partner import res_partner


class ResPartner(res_partner):

    delivery_lead_time = fields.Integer("Delivery lead time")

    def write(self, vals):
        result = super().write(vals)
        if "delivery_lead_time" in vals:
            self._propagate_delivery_lead_time()
        return result

    def _propagate_delivery_lead_time(self):
        """
        When the delivery lead time change on the supplier,.

        we have to overwrite the delay on each supplier info for this supplier
        :return:
        """
        supplierinfo_model = self.env["product.supplierinfo"]
        for rec in self:
            if not rec.delivery_lead_time:
                continue
            suppliers_info = supplierinfo_model.search([("partner_id", "=", rec.id)])
            suppliers_info.write({"delay": rec.delivery_lead_time})
