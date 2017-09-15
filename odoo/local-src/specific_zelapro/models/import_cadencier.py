from odoo import api, models


class ImportAlcyon(models.Model):
    _name = 'import.alcyon'

    @api.multi
    def init_import(self):
        print
