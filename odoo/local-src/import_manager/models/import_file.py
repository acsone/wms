# -*- coding: utf-8 -*-
# © 2017 Okia SPRL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
import re
import os
import traceback
import shutil
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
    is_regex = fields.Boolean('Filename with regex')
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
            import_file.get_filename_pattern(self.filename)

    @api.model
    def get_filename_pattern(self, filename, now_overwrite=None):
        """
        This method will return the filename of the file to import.
        Often files to import have a structured format.

        ######## With a date ########
        The file to import is "20170924_Customers.csv"
            - 20170924 is the date of today
            - _Customers.csv is the fixed part
        To use the date in the filename you can use datetime directive.
        (https://docs.python.org/2/library/datetime
        .html#strftime-and-strptime-behavior)

        By default, the datetime of "now" will be used to format datetime
        directives. You can overwrite the datetime of now with
        the param "now_overwrite"
        In this example, the filename will be "%Y%m%d_Customers.csv"

        ######## Simple filename ########
        The file to import is "ImportCustomer.csv"
            - ImportCustomer is the fixed part
        In this example, the filename will be "ImportCustomer.csv"
        :param filename: The filename
        :param now_overwrite: To overwrite the datetime of now (used in tests)
        :return:
        """

        # Check if the filename contains the extension
        if '.' not in filename:
            raise UserError(_('The filename must contain the extension'))

        # Use the datetime send in params or "now" (datetime)
        now = now_overwrite or datetime.now()

        # Datetime directives contain only "%" with a letter (eg: %Y, %m, ...)
        date_directive_regex = r'(%[a-zA-Z])'
        # To format date we will extract these directives
        result = re.findall(date_directive_regex, filename)
        # If the filename doesn't contain datetime directives
        # we can directly return the filename
        if not result:
            return filename

        # For each datetime directive (eg: %Y, %m, %d, ...), retrieve the value
        # and replace the directive by the value
        # Eg: the filename is %Y%m%d_customers.csv
        # The regex will return ['%Y', '%m', '%d']
        # First iteration: evaluation of %Y => 2017; replace %Y by 2017
        for date_format in result:
            try:
                value = now.strftime(date_format)
            except:
                raise UserError(_('The filename is not valid.'
                                  'Please check the part "%s"') % date_format)

            filename = filename.replace(date_format, value)

        return filename

    @api.constrains('importer')
    def check_importer(self):
        for import_file in self:
            try:
                self.env[import_file.importer]
            except:
                raise UserError(_('The importer (model name) "%s" '
                                  'doesn\'t exist') % import_file.importer)

    @api.model
    def execute_all_import(self):
        files = self.search([], order="sequence")
        files.execute_import()

    @api.multi
    def execute_import(self):
        self.ensure_one()

        _logger.info(_('Start the import %s') % self.name)

        config_obj = self.env['ir.config_parameter']
        import_model = self.env[self.importer]

        import_path = config_obj.get_param('import.import_in_path')
        if not import_path:
            raise UserError(_('Please defines the import path in imports '
                              'configuration before execute the first import')
                            )

        import_out_path = config_obj.get_param('import.import_out_path')
        if not os.path.isdir(import_out_path):
            os.makedirs(import_out_path)

        import_failure_path = \
            config_obj.get_param('import.import_failure_path')
        if not os.path.isdir(import_failure_path):
            os.makedirs(import_failure_path)

        filename_pattern = self.get_filename_pattern(self.filename)
        files_to_import = []
        for filename in os.listdir(import_path):
            file_path = os.path.join(import_path, filename)
            if self.is_regex and re.match(filename_pattern, filename):
                files_to_import.append(file_path)
            elif filename == filename_pattern:
                files_to_import.append(file_path)

        if not files_to_import:
            return

        # TODO Implement multiple imports
        if len(files_to_import) > 1:
            files_to_import = files_to_import[:1]

        for file_to_import in files_to_import:
            # Load the file in DB
            if self.file_type == 'csv':
                logger_id = \
                    import_model.init_csv_file(file_to_import, self.id)
            else:
                shutil.move(file_to_import, import_failure_path)
                raise UserError(_('File type %s unknown') % self.file_type)

            if not logger_id:
                shutil.move(file_to_import, import_failure_path)
                return
            logger = self.env['import.logger'].browse(logger_id)

            try:
                # Execute the import
                result = import_model.execute_import(logger_id)
                if result:
                    shutil.move(file_to_import, import_out_path)
                    self.env['import.logger'].browse(logger_id).write({
                        'state': 'success',
                        'date_end': fields.Datetime.now(),
                    })
                else:
                    shutil.move(file_to_import, import_failure_path)
                    logger.write({
                        'state': 'error',
                        'date_end': fields.Datetime.now(),
                    })
            except:
                shutil.move(file_to_import, import_failure_path)
                logger.line_ids.create({
                    'name': _('Not handled error during import execution'),
                    'level': 'error',
                    'traceback': traceback.format_exc(),
                    'logger_id': logger.id,
                })
                logger.write({
                    'state': 'error',
                    'date_end': fields.Datetime.now(),
                })
