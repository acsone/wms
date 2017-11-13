from odoo import fields, models


class PickingZone(models.Model):
    _name = 'picking.zone'

    name = fields.Char('Name', required=True, translate=True)
    code = fields.Char('Code', required=True)

    _sql_constraints = [
        ('unique_picking_zone',
         'unique (code)',
         'The picking zone code must be unique')
    ]
