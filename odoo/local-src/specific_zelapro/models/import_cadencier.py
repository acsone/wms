from odoo import api, fields, models, _


class ImportAlcyon(models.Model):
    _name = 'import.alcyon'

    @api.multi
    def init_import(self):
        print
