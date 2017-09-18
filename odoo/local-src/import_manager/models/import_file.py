# -*- coding: utf-8 -*-
# © 2017 Okia SPRL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
import re
import os
from datetime import datetime

from openerp import models, fields, api, _
from openerp.exceptions import UserError

_logger = logging.getLogger(__name__)


class ImportFile(models.Model):
    _description = "File to import"
    _name = "import.file"
    _order = "sequence"

    @api.multi
    def _compute_last_import(self):
        for import_file in self:
            logger = self.env['import.logger'].search(
                [('import_file_id', '=', import_file.id)],
                order='date_start desc',
                limit=1)
            if logger:
                import_file.last_import = logger.date_start

    name = fields.Char(required=True)
    importer = fields.Char(required=True,
                           help='This is the name of the class. '
                                'This class must inherit the abstract '
                                'class import.model')
    file_type = fields.Selection([('csv', 'CSV')],
                                 string='File type',
                                 default='csv',
                                 required=True)
    filename = fields.Char(
        required=True,
        help="The filename with extension. "
             "You can use datetime directives (like %Y, %m, ...)."
             "datetime.now() will be use to evaluate the filename.")
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    last_import = fields.Datetime(compute='_compute_last_import',
                                  readonly=True)
    logger_ids = fields.One2many('import.logger',
                                 'import_file_id',
                                 string='Loggers',
                                 readonly=True)

    @api.constrains('filename')
    def check_filename(self):
        for import_file in self:
            import_file.get_filename()

    @api.multi
    def get_filename(self):
        """
        Format the filename to evaluate datetime directives.
        E.G: The current date is 2017-09-24
        and the filename is %Y%m%d_MyFile.csv
        The method will return 20170924_MyFile.csv
        :return:
        """
        self.ensure_one()

        filename = self.filename
        if not len(filename.split('.')):
            raise UserError(_('The filename must contain the extension'))

        now = datetime.now()

        date_regex = r'(%[a-zA-Z])'
        result = re.match(date_regex, filename)
        if not result:
            return filename

        for date_format in result:
            try:
                value = now.strftime(date_format)
            except:
                raise UserError(_('The filename is not valid.'
                                  'Please check the part "%s"' % date_format))

            filename.replace(date_format, value)

        return filename

    @api.constrains('importer')
    @api.one
    def check_importer(self):
        try:
            self.env[self.importer]
        except:
            raise UserError(_('The importer (model name) '
                              '"%s" doesn\'t exist' % self.importer))

    @api.model
    def execute_all_import(self):
        files = self.search([], order="sequence")
        files.execute_import()

    @api.one
    def execute_import(self):
        _logger.info('Start the import %s' % self.name)

        config_obj = self.env['ir.config_parameter']
        import_model = self.env[self.importer]

        import_path = config_obj.get_param('import.import_path')
        if not import_path:
            raise UserError(_('Please defines the import path in imports '
                              'configuration before execute the first import')
                            )

        filename = self.get_filename()

        file_path = os.path.join(import_path, filename)
        if not os.path.isfile(file_path):
            self.env['import.logger'].create({
                'name': import_model._description or import_model._name,
                'file': file_path,
                'state': 'skip',
                'import_file_id': self.id,
            })
            return

        if self.file_type == 'csv':
            # Init the import
            logger_id = import_model.init_csv_file(file_path, self.id)
        else:
            raise UserError(_('File type %s unknown') % self.file_type)

        if not logger_id:
            return

        # Execute the import
        import_model.execute_import(logger_id)
