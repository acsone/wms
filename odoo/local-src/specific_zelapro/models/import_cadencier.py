from odoo import api, fields, models


class ImportCadencierHeader(models.Model):
    _name = 'import.cadencier.header'
    _inherit = 'import.model'

    sfesui = fields.Char()
    sfefou = fields.Char()
    sfenfo = fields.Char()
    sfedli = fields.Char()
    libdli = fields.Char()
    sfepds = fields.Char()
    sfemnt = fields.Char()
    sfemns = fields.Char()
    sfedbo = fields.Char()
    libdbo = fields.Char()
    sfests = fields.Char()

    @api.multi
    def execute_import(self, logger_id):
        """
        We don't need to import this file.
        :param logger_id:
        :return:
        """
        logger = self.env['import.logger'].browse(logger_id).write({
            'state': 'success'
        })


class ImportCadencier(models.Model):
    _name = 'import.cadencier'
    _inherit = 'import.model'

    sfdsui = fields.Char()
    sfdnli = fields.Char()
    sfdart = fields.Char()
    sfdden = fields.Char()
    sfdqte = fields.Char()
    sfdqmo = fields.Char()
    sfdpan = fields.Char()
    sfdpam = fields.Char()
    sfdr1o = fields.Char()
    sfdr1m = fields.Char()
    sfdr2o = fields.Char()
    sfdr2m = fields.Char()
    sfddli = fields.Char()
    libdli = fields.Char()
    sfddmo = fields.Char()
    libdmo = fields.Char()
    sfddbo = fields.Char()
    sfddbm = fields.Char()
    sfdsts = fields.Char()
    sfdtmi = fields.Char()
    sfdtma = fields.Char()
    sfdtst = fields.Char()
    sfdtbo = fields.Char()
    sfdtre = fields.Char()
    sfasua = fields.Char()
    sfanla = fields.Char()
    sfaqta = fields.Char()
    sfasup = fields.Char()
    sfanlp = fields.Char()
    sfaqtp = fields.Char()

    @api.multi
    def execute_import(self, logger_id):
        lines_query = """
        SELECT *
        FROM import_cadencier
        """

        so_obj = self.env['sale.order']



        logger = self.env['import.logger'].browse(logger_id).write({
            'state': 'success'
        })
