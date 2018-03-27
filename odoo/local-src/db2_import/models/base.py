from odoo import api, models


class Base(models.AbstractModel):
    _inherit = 'base'

    @api.model
    def create(self, vals):
        """ Allow to pass an `create_date` to insert this value in
        column `create_date`.

        The value will be inserted with an extra INSERT.

        Odoo automatically pops all MAGIC_COLUMNS like create_date.

        """
        init_vals = {}
        if 'create_date' in vals:
            init_vals['create_date'] = vals.pop('create_date')

        record = super(Base, self).create(vals)

        if init_vals:
            record._write(init_vals)

        return record
