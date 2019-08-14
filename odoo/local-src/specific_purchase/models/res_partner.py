# -*- coding: utf-8 -*-
# © 2017 Okia SPRL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    supplier_discount = fields.Float('Supplier discount %')

    purchase_manager_id = fields.Many2one(
        comodel_name='res.users', string='Purchase manager'
    )

    substitute_purchase_manager_id = fields.Many2one(
        comodel_name='res.users', string='Substitute purchase manager'
    )
    delivery_lead_time = fields.Integer('Delivery lead time')
    is_manage_day_1 = fields.Boolean('Monday')
    is_manage_day_2 = fields.Boolean('Tuesday')
    is_manage_day_3 = fields.Boolean('Wednesday')
    is_manage_day_4 = fields.Boolean('Thursday')
    is_manage_day_5 = fields.Boolean('Friday')
    is_manage_day_6 = fields.Boolean('Saturday')
    is_manage_day_7 = fields.Boolean('Sunday')

    @api.model
    def create(self, vals):
        record = super(ResPartner, self).create(vals)
        if 'delivery_lead_time' in vals:
            record._propagate_delivery_lead_time()
        return record

    @api.multi
    def write(self, vals):
        result = super(ResPartner, self).write(vals)
        if 'delivery_lead_time' in vals:
            self._propagate_delivery_lead_time()
        return result

    def _propagate_delivery_lead_time(self):
        """
        When the delivery lead time change on the supplier,
        we have to overwrite the delay on each supplier info for this supplier
        :return:
        """
        for partner in self:
            if not partner.delivery_lead_time:
                continue
            suppliers_info = self.env['product.supplierinfo'].search(
                [('name', '=', partner.id)]
            )
            suppliers_info.write({'delay': partner.delivery_lead_time})
